from .. import models
from ..Base import Base
from typing import List
import time
import json


class Cache(Base):
    def __init__(self, *args):
        # under no circumstances would cache data need to access Utility or the DB connection
        # but as this class is a critical method to keep the util working fine, we will inherit from the Base object.
        super().__init__(*args)

        # dict of discord (util) User objects -> not from d.py. Stored as a dict for easier searching.
        self.users = {}  # {user_id: User_object}
        self.maintenance_mode = False  # maintenance mode enabled
        self.maintenance_reason = None  # maintenance reason
        self.session_id = None  # current session id
        self.current_session = 0  # current session commands used
        self.total_used = None  # total amount of commands used
        self.session_time_format = None  # time format of current session for comparison
        self.bot_api_translation_calls = 0  # API Calls made directly from the bot for Translations per minute
        self.bot_api_idol_calls = 0  # API Calls made directly from the bot for Idols per minute
        self.n_words_per_minute = 0  # N Words per minute
        self.commands_per_minute = 0  # commands used in the current minute
        self.messages_received_per_minute = 0  # messages received per minute
        self.errors_per_minute = 0  # errors per minute
        self.wolfram_per_minute = 0  # wolfram calls per minute
        self.urban_per_minute = 0  # Urban dictionary calls per minute
        self.twitter_channel = None  # discord.TextChannel for auto twitter posts

        self.idol_images = {}  # { idol_id: [IreneUtility.models.Image] }

        self.channels_with_disabled_games = []

        # Amount of times a command has been used.
        self.command_counter = {}  # { command_name : amount_of_times_used }
        # Photo Count of groups
        self.group_photos = {}  # { group_id: photo_count }
        # Photo Count of idols
        self.idol_photos = {}  # { idol_id: photo_count }
        # All custom server prefixes
        self.server_prefixes = {}  # { server_id: server_prefix }
        """
        reset timer for idol photos (keeps track of command usage)
        {
            reset_time: date
            userid: [commands_used, time_since_last_command]
        }"""
        self.commands_used = {"reset_time": time.time()}
        # server to channels being logged
        """
        {
        server_id : {
                    send_all: 0 or 1,
                    logging_channel: channel_id,
                    channels: [channel_id, channel_id]
                    },
        ...
        }
        
        """
        self.logged_channels = {}
        # just a list of channels that are being logged with no correlation to the servers.
        # this exists to check if a channel is logged much quicker.
        self.list_of_logged_channels = []
        """
        Welcome Messages
        {
        server_id : {
            channel_id: channel_id,
            message: text,
            enabled: 0 or 1
            }
        }
        """
        self.welcome_messages = {}
        """
        Temp Channels
        {
        channel_id : seconds
        }
        """
        self.temp_channels = {}

        # TODO: convert to dict based on their idol/group id
        # list of idol objects
        self.idols = []
        # list of group objects
        self.groups = []

        # dict of restricted idol photo channels
        self.restricted_channels = {}  # {channelid : [server_id, sendall]}
        # contains all of the reported dead images
        self.dead_image_cache = {}  # {messageid : [dead_link, userid, idolid, is_guessing_game]}

        self.dead_image_channel = None  # Channel for all dead images to be sent to.
        self.bot_statuses = []

        # custom server commands
        self.custom_commands = {}  # {server_id: {command_name:info, command_name:info}}

        # Guessing Game Objects
        self.guessing_games = {}  # {channelid: Game}
        # Bias Game Objects
        self.bias_games = {}  # {channelid: Game}
        # BlackJack Game Objects
        self.blackjack_games: List[models.BlackJackGame] = []
        # UnScramble Game Objects
        self.unscramble_games = {}  # {channelid: Game}

        # Text channels to send Weverse updates to.
        self.weverse_channels = {}  # { community_name: [ [channel_id, role_id, comments_disabled, media_disabled] ] }

        # languages available, also the file names
        self.languages_available = ["en_us"]

        # Guessing Game User Scores
        self.guessing_game_counter = {}
        # {
        # user_id:
        #   {
        #       easy: int
        #       medium: int
        #       hard: int
        #   }
        # }

        self.unscramble_game_counter = {}
        # {
        # user_id:
        #   {
        #       easy: int
        #       medium: int
        #       hard: int
        #   }
        # }

        self.assignable_roles = {}  #
        # { server_id:
        #    {channel_id: channel_id,
        #    roles: [role_id, role_name]
        # }}

        self.main_youtube_instance = None  # Youtube Object that exists on start up.

        # Timezone to Locale dictionary
        with open('locale_by_timezone.json') as json_file:
            self.locale_by_timezone = json.load(json_file)

        # aliases for genders
        self.female_aliases = ['girl', 'girls', 'female', 'woman', 'women', 'girlgroup', 'girlgroups', 'f']
        self.male_aliases = ['male', 'm', 'men', 'boy', 'boys', 'boygroup', 'boygroups']

        # possible levels for guessing game
        self.difficulty_levels = ['easy', 'medium', 'hard']

        # sets of idols for guessing game
        self.idols_female = set()
        self.idols_male = set()
        self.idols_easy = set()
        self.idols_medium = set()
        self.idols_hard = set()

        # guessing game difficulty or gender selection
        # { selection_key_word : idol_set}
        self.difficulty_selection = {
            'easy': self.idols_easy,
            'e': self.idols_easy,
            'medium': self.idols_medium,
            'm': self.idols_medium,
            'hard': self.idols_hard,
            'h': self.idols_hard
        }
        self.gender_selection = {
            'female': self.idols_female,
            'male': self.idols_male,
            'all': set(self.idols)
        }

        #  guilds will soon have their own object, for now these will be separated.
        self.twitch_channels = {}  # {twitch_username: [guild ids]}
        self.twitch_guild_to_channels = {}  # guild_id: channel_id
        self.twitch_guild_to_roles = {}  # guild_id: role_id

        self.twitch_channels_is_live = {}  # twitch_username : false/true

        """
        User Notifications and Mod Mail are constantly iterated over, therefore we need a synced list
        apart from the information present in the user objects to stop the bot from being blocked/behind
        on future commands. These were removed and put into the user objects, but will now be placed back due to 
        this issue.
        """
        self.user_notifications = []
        # mod mail user and channel {user_id: channel_id}
        self.mod_mail = {}

        self.languages = {}  # language packs

        self.playing_cards = {}  # {card_id: [custom playing card 1, custom playing card 2]}

        # used for the loop to send idol photos to a text channel after t time.
        self.send_idol_photos = {}  # (text channel id OR discord.TextChannel) : [list of idol ids]

        self.member_ids_in_support_server = []  # [user ids]

        self.welcome_roles = {}  # d.py Guild object : d.py Role object

        # bracket position for bias game stored due to annoyance when using previous x and y values.
        # counting starts from left to right, bottom to top
        self.stored_bracket_positions = {
            1: {'img_size': (50, 50), 'pos': (30, 515)},
            2: {'img_size': (50, 50), 'pos': (100, 515)},
            3: {'img_size': (50, 50), 'pos': (165, 515)},
            4: {'img_size': (50, 50), 'pos': (230, 515)},
            5: {'img_size': (50, 50), 'pos': (320, 515)},
            6: {'img_size': (50, 50), 'pos': (390, 515)},
            7: {'img_size': (50, 50), 'pos': (455, 515)},
            8: {'img_size': (50, 50), 'pos': (525, 515)},
            9: {'img_size': (75, 75), 'pos': (55, 380)},
            10: {'img_size': (75, 75), 'pos': (185, 380)},
            11: {'img_size': (75, 75), 'pos': (340, 380)},
            12: {'img_size': (75, 75), 'pos': (475, 380)},
            13: {'img_size': (100, 100), 'pos': (110, 225)},
            14: {'img_size': (100, 100), 'pos': (390, 225)},
            15: {'img_size': (134, 130), 'pos': (235, 55)}
        }

        # Equivalent keyword for translate languages
        # { papago_code : lang_keyword_aliases }
        self.lang_keywords = {
            'ko': ['korean', 'ko', 'kr', 'korea', 'kor'],
            'en': ['en', 'eng', 'english'],
            'ja': ['jp', 'jap', 'japanese', 'japan'],
            'zh-CN': ['chinese', 'ch', 'zh-cn', 'zhcn', 'c', 'china'],
            'zh-TW': [],
            'es': ['es', 'espanol', 'spanish', 'sp'],
            'fr': ['french', 'fr', 'f', 'fren'],
            'vi': ['viet', 'vi', 'vietnamese', 'vietnam'],
            'th': ['th', 'thai', 'thailand'],
            'id': ['id', 'indonesian', 'indonesia', 'ind']
        }

        # General card description format
        # Create list if the attribute should be surrounded by two strings
        self.general_description = {
            'description': ['', '\n'],
            'id': 'ID: ',
            'gender': 'Gender: ',
            'photo_count': 'Photo Count: ',
        }

        # Group card description format
        # { field/attribute name : Card Display Format }
        # Create list if the attribute should be surrounded by two strings
        self.group_description = {
            'name': 'Name: ',
            'debut_date': 'Debut Date: ',
            'disband_date': 'Disband Date: ',
            'fandom': 'Fandom Name: ',
            'company': 'Company: ',
            'website': ['[Official Website](', ')']
        }

        # Idol card description format
        # Create list if the attribute should be surrounded by two strings
        self.idol_description = {
            'full_name': 'Full Name: ',
            'stage_name': 'Stage Name: ',
            'former_full_name': 'Former Full Name: ',
            'former_stage_name': 'Former Stage Name: ',
            'birth_date': 'Birth Date: ',
            'birth_country': 'Birth Country: ',
            'birth_city': 'Birth City: ',
            'height': ['Height: ', 'cm'],
            'zodiac': 'Zodiac Sign: ',
            'blood_type': 'Blood Type: ',
            'called': ['Called: ', ' times'],
            'difficulty': 'Guessing Game Difficulty: ',
        }

        # Website card description format
        # Create list if the attribute should be surrounded by two strings
        self.website_description = {
            'twitter': ['[Twitter](https://twitter.com/', ')'],
            'youtube': ['[Youtube](https://www.youtube.com/channel/', ')'],
            'melon': ['[Melon](https://www.melon.com/artist/song.htm?artistId=', ')'],
            'instagram': ['[Instagram](https://instagram.com/', ')'],
            'vlive': ['[V Live](https://channels.vlive.tv/', ')'],
            'spotify': ['[Spotify](https://open.spotify.com/artist/', ')'],
            'fancafe': ['[FanCafe](https://m.cafe.daum.net/', ')'],
            'facebook': ['[Facebook](https://www.facebook.com/', ')'],
            'tiktok': ['[TikTok](https://www.tiktok.com/', ')'],
        }

        self.stop_phrases = ['stop', 'end', 'quit']
        self.dead_image_phrases = ['dead', 'report']
        self.skip_phrases = ['skip', 'pass']

        self.year_aliases = ["years", "year", "yr", "y"]
        self.month_aliases = ["months", "month", "mo"]
        self.week_aliases = ["weeks", "week", "wk"]
        self.day_aliases = ["days", "day", "d"]
        self.hour_aliases = ["hours", "hour", "hrs", "hr", "h"]
        self.minute_aliases = ["minutes", "minute", "mins", "min", "m"]
        self.second_aliases = ["seconds", "second", "secs", "sec", "s"]
        self.time_units = [[self.year_aliases, 31536000], [self.month_aliases, 2592000], [self.week_aliases, 604800],
                           [self.day_aliases, 86400], [self.hour_aliases, 3600], [self.minute_aliases, 60],
                           [self.second_aliases, 1]]
        self.all_time_aliases = [alias for time_unit in self.time_units for alias in time_unit[0]]

        # phrases that would trigger a message check in guessing game.
        self.gg_msg_phrases = self.stop_phrases + self.dead_image_phrases + self.skip_phrases

        self.interaction_list = [
            'slap',
            'kiss',
            'lick',
            'hug',
            'punch',
            'spit',
            'pat',
            'cuddle',
            'pullhair',
            'choke',
            'stepon',
            'stab'
        ]

        self.eight_ball_responses = [
            # Positive 13
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            ":thumbsup:",
            "Well, duh",
            "Of course, that was a stupid question.",

            # Neutral 7
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Why the fuck are you asking me you dumb rat.",
            "You should already know this you 바보.",

            # Negative 10
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
            ":thumbsdown:",
            "Are you kidding?",
            "Don't bet on it.",
            "Forget about it.",
            "It's just not meant to be."]
