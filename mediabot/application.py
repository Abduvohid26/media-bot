import asyncio
import typing
from telegram import Bot
from telegram.ext import ApplicationBuilder
from mediabot.features.instance.model import Instance as InstanceModel, InstanceFeatures, _Instance, InstanceQuota
from mediabot.features.required_join.handlers import RequiredJoin, RequiredJoinKind, required_join_is_member
from mediabot.instance import Instance
from mediabot.features.language.model import Language
from mediabot.features.account.model import Account
from mediabot.features.advertisement.model import Advertisement
from mediabot.cache import redis
from mediabot.env import TELEGRAM_BOT_API_BASE_URL

from mediabot.env import API_ACCESS_TOKEN
from aiohttp import web as http

DOWNLOAD_HTML = open("static/download.html", "r").read()

class Application:
  # instance cache
  instances: dict[int, Instance] = {}

  # http server
  http_server: http.Application

  def __init__(self):
    self.http_server = http.Application()
    self.bootstrap_api()
    self.http_server.on_startup.append(self._bootstrap_instances)

  def bootstrap_api(self):
    assert self.http_server

    self.http_server.add_routes([
      # http.get("/download", self._download),
      http.get("/instances", self._instances_route_handler),
      http.get("/instances/{instance_id}", self._instance_route_handler),

      http.get("/instance/cache", self._media_cache_lookup_route_handler),

      # http.post("/instance/bootstrap", self._instance_bootstrap_handler),
      http.post("/instances", self._instance_create_route_handler),
      http.post("/instances/{instance_id}/enable", self._instance_enable_route_handler),
      http.post("/instances/{instance_id}/bootstrap", self._instance_bootstrap_route_handler),
      http.post("/instances/{instance_id}/disable", self._instance_disable_route_handler),
      http.post("/instances/{instance_id}/webhook", self._instance_webhook_handler),
      http.post("/instances/{instance_id}/features/{feature}/enable", self._instance_enable_feature_handler),
      http.post("/instances/{instance_id}/features/{feature}/disable", self._instance_disable_feature_handler),

      http.get("/instances/{token}/required-joins", self._instance_required_joins),
      http.get("/instances/{token}/advertisements", self._instance_advertisements),

      # http.get("/tgdata{absolute_path}", self._static_file_handler)
    ])

  async def _bootstrap_instances(self, http_server: http.Application):
    database_instances = await InstanceModel.get_all()

    for database_instance in database_instances:
      if not database_instance.is_enabled:
        return

      try:
        instance = Instance(database_instance)
        await instance.bootstrap()
        self.instances[database_instance.id] = instance
      except:
        pass

  def _create_standard_response(self, data=None, error=None, status_code=http.HTTPOk.status_code):
    return http.json_response({"data": data, "error": error}, status=status_code)

  def _check_access_token(self, request: http.Request):
    access_token = request.query.get("access_token", None)

    if not access_token:
      raise http.HTTPUnauthorized()

    if access_token != API_ACCESS_TOKEN:
      raise http.HTTPUnauthorized()

  # GET /download
  # async def _download(self, request: http.Request) -> http.Response:
  #   query_params = request.match_info

  #   if not "instance_id" in query_params or not query_params["instance_id"].isnumeric():
  #     return http.HTTPBadRequest()

  #   if not "chat_id" in query_params or not query_params["chat_id"].isnumeric():
  #     return http.HTTPBadRequest()

  #   if not "user_id" in query_params or not query_params["user_id"].isnumeric():
  #     return http.HTTPBadRequest()

  #   instance_id = int(query_params["instance_id"])
  #   chat_id = int(query_params["chat_id"])
  #   user_id = int(query_params["user_id"])
  #   track_id = query_params.get("track_id", None)
  #   video_id = query_params.get("video_id", None)

  #   if not track_id and not video_id:
  #     return http.HTTPBadRequest()

  #   if not instance_id in self.instances:
  #     return http.HTTPBadRequest()

  #   instance = self.instances[instance_id]

  #   event_loop = asyncio.get_event_loop()

  #   if track_id:
  #     event_loop.create_task(instance.process_track_download_web(chat_id, user_id, track_id))
  #   elif video_id:
  #     event_loop.create_task(instance.process_track_download_web(chat_id, user_id, video_id))

  #   return http.Response(body=DOWNLOAD_HTML)

  async def _instance_bootstrap(self, instance: _Instance):
    if instance.id in self.instances:
      await self.instances[instance.id].close()

    await asyncio.sleep(2)

    new_instance = Instance(instance)

    await new_instance.bootstrap()

    self.instances[instance.id] = new_instance

  # GET /instance/cache route handler
  # TODO: bad code, refactor me
  async def _media_cache_lookup_route_handler(self, request: http.Request) -> http.Response:
    media_id = request.query.get("media_id", None)
    type = request.query.get("type", "track")

    if not media_id:
      return self._create_standard_response(error="Media id is missing", status_code=http.HTTPBadRequest.status_code)

    if not type in ["track", "youtube"]:
      return self._create_standard_response(error="Invalid cache type", status_code=http.HTTPBadRequest.status_code)

    # TODO: slow operation
    keys = await redis.keys(f'{type}:file_id:[0-9]*:{media_id}')
    if not keys:
      return self._create_standard_response(error="No cache found", status_code=http.HTTPNotFound.status_code)

    instance_id = int(keys[0].split(":")[2])
    instance = await InstanceModel.get(instance_id)

    if not instance or not instance.is_enabled:
      return self._create_standard_response(error="Cache found but bot is disabled", status_code=http.HTTPNotFound.status_code)

    return self._create_standard_response({"username": instance.username})

  async def _instance_advertisements(self, request: http.Request) -> http.Request:
    token = str(request.match_info["token"])
    account_telegram_id = request.query.get("account_telegram_id", "")
    kind = request.query.get("kind", Advertisement.KIND_NONE)

    if not account_telegram_id or account_telegram_id.isdigit() == False:
      return self._create_standard_response("Invalid account_telegram_id query parameter", status_code=http.HTTPBadRequest.status_code)

    if not kind.isdigit() or not (int(kind) in Advertisement.KINDS):
      return self._create_standard_response("Invalid kind", status_code=http.HTTPBadRequest.status_code)

    target_instance = await InstanceModel.get_by_token(token)
    if not target_instance:
      return self._create_standard_response("Instance not found", status_code=http.HTTPBadRequest.status_code)

    target_account = await Account.get(target_instance.id, account_telegram_id)
    if not target_account:
      return self._create_standard_response("Account not found", status_code=http.HTTPBadRequest.status_code)

    advertisements = await Advertisement.get_all_messages_for(target_instance.id, kind, target_account.id)
    return self._create_standard_response([advertisement.to_json() for advertisement in advertisements])

  async def _instance_required_joins(self, request: http.Request) -> http.Request:
    token = str(request.match_info["token"])
    account_telegram_id = request.query.get("account_telegram_id", "")
    account_language_origin = request.query.get("account_language_origin", None)
    kind = request.query.get("kind", RequiredJoinKind.MEDIA_QUERY)

    if not account_telegram_id or account_telegram_id.isdigit() == False:
      return self._create_standard_response("Invalid account_telegram_id query parameter", status_code=http.HTTPBadRequest.status_code)

    if account_language_origin is not None and account_language_origin.isdigit() == False:
      return self._create_standard_response("Invalid account_language_origin query parameter", status_code=http.HTTPBadRequest.status_code)

    if not (kind in [RequiredJoinKind.MEDIA_QUERY, RequiredJoinKind.MEDIA_DOWNLOAD]):
      return self._create_standard_response("Invalid kind", status_code=http.HTTPBadRequest.status_code)

    target_instance = await InstanceModel.get_by_token(token)
    if not target_instance:
      return self._create_standard_response("Instance not found", status_code=http.HTTPBadRequest.status_code)

    target_account = await Account.get(target_instance.id, account_telegram_id)
    if not target_account:
      return self._create_standard_response("Account not found", status_code=http.HTTPBadRequest.status_code)

    telegram_bot = Bot(target_instance.token, TELEGRAM_BOT_API_BASE_URL)

    required_joins = await RequiredJoin.get_all_for(target_instance.id, target_account.id, account_language_origin, kind)

    # keep only "not joined chats" so the caller doesn't have to manually check the membership
    required_joins = [required_join for required_join in required_joins \
        if not (await required_join_is_member(telegram_bot, target_account.telegram_id, required_join))]

    return self._create_standard_response([required_join.to_json() for required_join in required_joins])

  async def _instance_bootstrap_route_handler(self, request: http.Request) -> http.Response:
    instance_id = str(request.match_info["instance_id"])

    self._check_access_token(request)

    # check if instance id is is numeric
    if not instance_id.isnumeric():
      return self._create_standard_response(error="invalid instance id", status_code=http.HTTPBadRequest.status_code)

    instance_object = await InstanceModel.get(instance_id)
    if not instance_object:
      return self._create_standard_response(error="instance not found", status_code=http.HTTPNotFound.status_code)

    await self._instance_bootstrap(instance_object)

    return self._create_standard_response(True)

  # POST /instances/:instance/webhook route handlers
  async def _instance_webhook_handler(self, request: http.Request) -> http.Response:
    instance_id = str(request.match_info["instance_id"])

    # check if instance is is numeric
    if not instance_id.isnumeric():
      return self._create_standard_response(error="invalid instance id", status_code=http.HTTPBadRequest.status_code)

    instance_id = int(instance_id)
    update_object = await request.json()

    instance_object = await InstanceModel.get(instance_id)

    if not instance_object:
      return self._create_standard_response(error="instance not found", status_code=http.HTTPNotFound.status_code)

    if not instance_object.is_enabled:
      return self._create_standard_response(True)

    if instance_id not in self.instances:
      self.instances[instance_id] = Instance(instance_object)
      await self.instances[instance_id].bootstrap()

    if "bootstrap" in self.instances[instance_id].botapp.bot_data:
      del self.instances[instance_id].botapp.bot_data["bootstrap"]

      # close the old insrtance
      await self.instances[instance_id].close()
      del self.instances[instance_id]

      # wait for some time to not hit the limit
      await asyncio.sleep(2)

      # initialize new one and bootstrap
      self.instances[instance_id] = Instance(instance_object)
      await self.instances[instance_id].bootstrap()

    await self.instances[instance_id].process_update(update_object)

    return self._create_standard_response(True)

  # POST /instances/:instance/features/:feature/enable
  async def _instance_enable_feature_handler(self, request: http.Request) -> http.Response:
    instance_id = int(request.match_info["instance_id"])
    feature = str(request.match_info["feature"])

    self._check_access_token(request)

    target_instance = await InstanceModel.get(instance_id)
    if not target_instance:
      return self._create_standard_response(error="instance not found", status_code=http.HTTPNotFound.status_code)

    feature = feature.upper()

    if feature == InstanceFeatures.BROADCAST.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.BROADCAST)
    elif feature == InstanceFeatures.COMMAND.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.COMMAND)
    elif feature == InstanceFeatures.REQUIRED_JOIN.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.REQUIRED_JOIN)
    elif feature == InstanceFeatures.ADVERTISEMENT.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.ADVERTISEMENT)
    elif feature == InstanceFeatures.JOIN_REQUEST.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.JOIN_REQUEST)
    elif feature == InstanceFeatures.REFERRAL.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.REFERRAL)
    elif feature == InstanceFeatures.MESSAGE.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.MESSAGE)
    elif feature == InstanceFeatures.INSTAGRAM.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.INSTAGRAM)
    elif feature == InstanceFeatures.TIKTOK.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.TIKTOK)
    elif feature == InstanceFeatures.TRACK_SEARCH.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.TRACK_SEARCH)
    elif feature == InstanceFeatures.TRACK_DOWNLOAD.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.TRACK_DOWNLOAD)
    elif feature == InstanceFeatures.TRACK_POPULAR_TRACKS.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.TRACK_POPULAR_TRACKS)
    elif feature == InstanceFeatures.RECOGNIZE_FROM_VOICE.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.RECOGNIZE_FROM_VOICE)
    elif feature == InstanceFeatures.VIDEO_SEARCH.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.VIDEO_SEARCH)
    elif feature == InstanceFeatures.TIKTOK.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.TIKTOK)
    elif feature == InstanceFeatures.TRACK_RECOGNIZE_FROM_VOICE.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.TRACK_RECOGNIZE_FROM_VOICE)
    elif feature == InstanceFeatures.TRACK_RECOGNIZE_FROM_VIDEO_NOTE.name:
      await InstanceModel.enable_feature(instance_id, InstanceFeatures.TRACK_RECOGNIZE_FROM_VIDEO_NOTE)
    else:
      return self._create_standard_response(error="invalid feature", status_code=http.HTTPBadRequest.status_code)
    
    self.instances.pop(instance_id, None)

    return self._create_standard_response(True)

  # POST /instances/:instance/features/:feature/disable
  async def _instance_disable_feature_handler(self, request: http.Request) -> http.Response:
    instance_id = int(request.match_info["instance_id"])
    feature = str(request.match_info["feature"])

    self._check_access_token(request)

    target_instance = await InstanceModel.get(instance_id)
    if not target_instance:
      return self._create_standard_response(error="instance not found", status_code=http.HTTPNotFound.status_code)

    # bad but works
    feature = feature.upper()

    if feature == InstanceFeatures.BROADCAST.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.BROADCAST)
    elif feature == InstanceFeatures.COMMAND.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.COMMAND)
    elif feature == InstanceFeatures.REQUIRED_JOIN.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.REQUIRED_JOIN)
    elif feature == InstanceFeatures.ADVERTISEMENT.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.ADVERTISEMENT)
    elif feature == InstanceFeatures.JOIN_REQUEST.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.JOIN_REQUEST)
    elif feature == InstanceFeatures.REFERRAL.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.REFERRAL)
    elif feature == InstanceFeatures.MESSAGE.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.MESSAGE)
    elif feature == InstanceFeatures.INSTAGRAM.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.INSTAGRAM)
    elif feature == InstanceFeatures.TIKTOK.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.TIKTOK)
    elif feature == InstanceFeatures.TRACK_SEARCH.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.TRACK_SEARCH)
    elif feature == InstanceFeatures.TRACK_DOWNLOAD.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.TRACK_DOWNLOAD)
    elif feature == InstanceFeatures.TRACK_POPULAR_TRACKS.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.TRACK_POPULAR_TRACKS)
    elif feature == InstanceFeatures.RECOGNIZE_FROM_VOICE.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.RECOGNIZE_FROM_VOICE)
    elif feature == InstanceFeatures.VIDEO_SEARCH.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.VIDEO_SEARCH)
    elif feature == InstanceFeatures.TIKTOK.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.TIKTOK)
    elif feature == InstanceFeatures.TRACK_RECOGNIZE_FROM_VOICE.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.TRACK_RECOGNIZE_FROM_VOICE)
    elif feature == InstanceFeatures.TRACK_RECOGNIZE_FROM_VIDEO_NOTE.name:
      await InstanceModel.disable_feature(instance_id, InstanceFeatures.TRACK_RECOGNIZE_FROM_VIDEO_NOTE)
    else:
      return self._create_standard_response(error="invalid feature", status=http.HTTPBadRequest.status_code)

    self.instances.pop(instance_id, None)

    return self._create_standard_response(True)

  # POST /instances/:instance/enable route handler
  async def _instance_enable_route_handler(self, request: http.Request) -> http.Response:
    instance_id = str(request.match_info["instance_id"])

    self._check_access_token(request)

    if not instance_id.isnumeric():
      return self._create_standard_response(error="invalid instance id", status_code=http.HTTPBadRequest.status_code)

    instance_id = int(instance_id)

    instance = await InstanceModel.get(instance_id)
    if not instance:
      return self._create_standard_response(error="instance not found", status_code=http.HTTPNotFound.status_code)

    await InstanceModel.enable_instance(instance_id)

    await self._instance_bootstrap(instance)

    return self._create_standard_response(True)

  # POST /instances/:instance/disable route handler
  async def _instance_disable_route_handler(self, request: http.Request) -> http.Response:
    instance_id = str(request.match_info["instance_id"])

    self._check_access_token(request)

    if not instance_id.isnumeric():
      return self._create_standard_response(error="invalid instance id", status_code=http.HTTPBadRequest.status_code)

    instance_id = int(instance_id)

    await InstanceModel.disable_instance(instance_id)

    if instance_id in self.instances:
      await self.instances[instance_id].close()
      del self.instances[instance_id]

    return self._create_standard_response(True)

  # GET /instances/:instance route handler
  async def _instance_route_handler(self, request: http.Request) -> http.Response:
    instance_id = int(request.match_info["instance_id"])

    self._check_access_token(request)

    instance = await InstanceModel.get(instance_id)
    if not instance:
      return self._create_standard_response(error="instance not found", status_code=http.HTTPNotFound.status_code)

    return self._create_standard_response(instance.to_json())

  # GET /instances route handler
  async def _instances_route_handler(self, request: http.Request) -> http.Response:
    self._check_access_token(request)

    instances = await InstanceModel.get_all()

    return self._create_standard_response([instance.to_json() for instance in instances])

  # POST /instances route handler
  async def _instance_create_route_handler(self, request: http.Request) -> http.Response:
    self._check_access_token(request)

    request_body = typing.cast(dict, await request.json())
    token = request_body.get("token", None)

    track_search_feature_enabled                     = typing.cast(bool, request_body.get(InstanceFeatures.TRACK_SEARCH.value, False))
    track_download_feature_enabled                   = typing.cast(bool, request_body.get(InstanceFeatures.TRACK_DOWNLOAD.value, False))
    track_recognize_from_voice_feature_enabled       = typing.cast(bool, request_body.get(InstanceFeatures.TRACK_RECOGNIZE_FROM_VOICE.value, False))
    track_recognize_from_audio_feature_enabled       = typing.cast(bool, request_body.get(InstanceFeatures.TRACK_RECOGNIZE_FROM_AUDIO.value, False))
    track_recognize_from_video_note_feature_enabled  = typing.cast(bool, request_body.get(InstanceFeatures.TRACK_RECOGNIZE_FROM_VIDEO_NOTE.value, False))
    track_quota                                      = typing.cast(bool, request_body.get(InstanceQuota.TRACK.value, 100))

    instagram_feature_enabled                        = typing.cast(bool, request_body.get(InstanceFeatures.INSTAGRAM.value, False))
    instagram_recognize_track_feature_enabled        = typing.cast(bool, request_body.get(InstanceFeatures.INSTAGRAM_RECOGNIZE_TRACK.value, False))
    instagram_quota                                  = typing.cast(bool, request_body.get(InstanceQuota.INSTAGRAM.value, 100))

    tiktok_feature_enabled                           = typing.cast(bool, request_body.get(InstanceFeatures.TIKTOK.value, False))
    tiktok_recognize_track_feature_enabled           = typing.cast(bool, request_body.get(InstanceFeatures.TIKTOK_RECOGNIZE_TRACK.value, False))
    tiktok_quota                                     = typing.cast(bool, request_body.get(InstanceQuota.TIKTOK.value, 100))

    twitter_feature_enabled                          = typing.cast(bool, request_body.get(InstanceFeatures.TWITTER, False))
    likee_feature_enabled                            = typing.cast(bool, request_body.get(InstanceFeatures.LIKEE, False))
    tumblr_feature_enabled                           = typing.cast(bool, request_body.get(InstanceFeatures.TUMBLR, False))
    pinterest_feature_enabled                        = typing.cast(bool, request_body.get(InstanceFeatures.PINTEREST, False))
    facebook_feature_enabled                        = typing.cast(bool, request_body.get(InstanceFeatures.FACEBOOK, False))

    youtube_search_feature_enabled                   = typing.cast(bool, request_body.get(InstanceFeatures.YOUTUBE_SEARCH.value, False))
    youtube_download_feature_enabled                 = typing.cast(bool, request_body.get(InstanceFeatures.YOUTUBE_DOWNLOAD.value, False))
    youtube_recognize_track_feature_enabled          = typing.cast(bool, request_body.get(InstanceFeatures.YOUTUBE_RECOGNIZE_TRACK.value, False))
    youtube_quota                                    = typing.cast(bool, request_body.get(InstanceQuota.YOUTUBE.value, 100))

    broadcast_feature_enabled                        = typing.cast(bool, request_body.get(InstanceFeatures.BROADCAST.value, False))
    comamnd_feature_enabled                          = typing.cast(bool, request_body.get(InstanceFeatures.COMMAND.value, False))
    required_join_feature_enabled                    = typing.cast(bool, request_body.get(InstanceFeatures.REQUIRED_JOIN.value, False))
    advertisement_feature_enabled                    = typing.cast(bool, request_body.get(InstanceFeatures.ADVERTISEMENT.value, False))
    join_request_feature_enabled                     = typing.cast(bool, request_body.get(InstanceFeatures.JOIN_REQUEST.value, False))
    referral_feature_enabled                         = typing.cast(bool, request_body.get(InstanceFeatures.REFERRAL.value, False))
    web_feature_enabled                              = typing.cast(bool, request_body.get(InstanceFeatures.WEB.value, False))

    if not token:
      return self._create_standard_response(error="invalid token", status_code=http.HTTPBadRequest.status_code)

    instance_exists = await InstanceModel.exists_by_token(token)
    if instance_exists:
      return self._create_standard_response(error="instance already exists with this token", status_code=http.HTTPBadRequest.status_code)

    # try to initiate telegram bot with this token and get username
    telegram_bot = ApplicationBuilder().token(token).updater(None).build().bot
    try:
      me = await telegram_bot.get_me()
      if not me.username:
        return self._create_standard_response(error="invalid bot username", status_code=http.HTTPBadRequest.status_code)
      bot_username = me.username
    except Exception:
      return self._create_standard_response(error="invalid bot token", status_code=http.HTTPBadRequest.status_code)

    created_instance_id = await InstanceModel.create(
      token=token,
      username=bot_username,

      track_search_feature_enabled=track_search_feature_enabled,
      track_download_feature_enabled=track_download_feature_enabled,
      track_recognize_from_audio_feature_enabled=track_recognize_from_audio_feature_enabled,
      track_recognize_from_voice_feature_enabled=track_recognize_from_voice_feature_enabled,
      track_recognize_from_video_note_feature_enabled=track_recognize_from_video_note_feature_enabled,
      track_quota=track_quota,

      instagram_feature_enabled=instagram_feature_enabled,
      instagram_recognize_track_feature_enabled=instagram_recognize_track_feature_enabled,
      instagram_quota=instagram_quota,

      tiktok_feature_enabled=tiktok_feature_enabled,
      tiktok_recognize_track_feature_enabled=tiktok_recognize_track_feature_enabled,
      tiktok_quota=tiktok_quota,

      twitter_feature_enabled=twitter_feature_enabled,
      likee_feature_enabled=likee_feature_enabled,
      tumblr_feature_enabled=tumblr_feature_enabled,
      pinterest_feature_enabled=pinterest_feature_enabled,
      facebook_feature_enabled=facebook_feature_enabled,

      youtube_search_feature_enabled=youtube_search_feature_enabled,
      youtube_download_feature_enabled=youtube_download_feature_enabled,
      youtube_recognize_track_feature_enabled=youtube_recognize_track_feature_enabled,
      youtube_quota=youtube_quota,

      broadcast_feature_enabled=broadcast_feature_enabled,
      command_feature_enabled=comamnd_feature_enabled,
      required_join_feature_enabled=required_join_feature_enabled,
      advertisement_feature_enabled=advertisement_feature_enabled,
      join_request_feature_enabled=join_request_feature_enabled,
      referral_feature_enabled=referral_feature_enabled,

      web_feature_enabled=web_feature_enabled,
    )

    await self._instance_create_defaults(created_instance_id)

    return http.json_response({"id": created_instance_id})

  async def _instance_create_defaults(self, instance_id: int):
    # create default languages
    await Language.create(instance_id, "🇺🇿 O'zbekcha", "uz")
    await Language.create(instance_id, "🇷🇺 Русский", "ru")
    await Language.create(instance_id, "🇺🇸 English", "en")
    await Language.create(instance_id, "🇩🇪 Deutsch", "de")
    await Language.create(instance_id, "🇰🇿 Қазақ", "kz")
    await Language.create(instance_id, "🇨🇳 中文", "cn")
    await Language.create(instance_id, "🇮🇳 हिन्दी", "in")
    await Language.create(instance_id, "🇧🇷 Português", "br")
    await Language.create(instance_id, "🇮🇩 Bahasa Indonesia", "id")
    await Language.create(instance_id, "🇪🇸 Español", "es")
    await Language.create(instance_id, "🇮🇹 Italiano", "it")
    await Language.create(instance_id, "🇺🇦 Українська", "ua")
    await Language.create(instance_id, "🇹🇷 Türkçe", "tr")
    await Language.create(instance_id, "🇫🇷 Français", "fr")
    await Language.create(instance_id, "🇵🇭 Filipino", "ph")
    await Language.create(instance_id, "🇲🇾 Bahasa Malaysia", "my")
