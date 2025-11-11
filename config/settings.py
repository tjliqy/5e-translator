# import logging
from logger_config import logger
import os

from dotenv import load_dotenv
from datetime import datetime
# 加载项目根目录下的 .env 文件
load_dotenv()

DB_CONFIG = {
    'HOST': os.getenv("DB_HOST"),
    'PORT': int(os.getenv("DB_PORT")),
    'USER': os.getenv("DB_USER"),
    'PASSWORD': os.getenv("DB_PASSWORD"),
    'DATABASE': os.getenv("DB_DATABASE"),
}

DS_KEY = os.getenv("DS_KEY")
# logger = logging.getLogger(__name__)
# logging_file_name = f"/data/5e-translator/log/demo_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
# logging.basicConfig(
#     level=logging.INFO,  # 设置日志输出格式
#     filename=logging_file_name,  # log日志输出的文件位置和文件名
#     filemode="w",  # 文件的写入格式，w为重新写入文件，默认是追加
#     format="%(asctime)s - %(name)s - %(levelname)-9s - %(filename)-8s : %(lineno)s line - %(message)s"  # 日志输出的格式
#     # -8表示占位符，让输出左对齐，输出长度都为8位
#     ,
#     datefmt="%Y-%m-%d %H:%M:%S",  # 时间输出的格式
# )
BASE_PATH = "/data/"
EN_PATH=os.getenv("5ETOOLS_EN_PATH")
OUT_PATH=os.getenv("OUTPUT_PATH")
DIC_PATH=OUT_PATH+"/dictionary.json"

PLU_EN_PATH="/root/workspace/src/plutonium/data-bak"

FORCE_TRANSLATE_STR=["ox"]

SKIP_PATTERN=[r'^Math\.',r'\.json$',r'\.mp3$',r'\.pdf$',r'\.svg$',r'^system\.',r'^[+*\-\dd]+$',r'\.webp$',r'\.glb$',r'^col-', r'^\{@dice [0-9d+\-×*/; ]+\}$', r'^[0-9d+\-–×*/%％;\[\]& ]*$',r'^https://.+',r'^http://.+', r'^www\..+',r'^Challenge Rating=.+',r'^@abilities\..*',r'^@classes\..*']
SKIP_PREFIX=['source=','level=','class=','subclass=','challenge rating=','speed type=','type=','miscellaneous=','category=','school=','components & miscellaneous=', 'Components & Miscellaneous=','spell attack=','tag=','search=','Type=','damage type=','Feature Type=','Base Species=', 'environment=','strength=','property=']
TOTAL_SKIP_PREFIX=['rarity=']
SKIP_SUFFIX=['#2','#c','#x']
SKIP_KEYS=['source', 'fonts', 'type', 'path', 'id', 'href','mode','_meta','group','armor','trapHazType','vehicleType','rarity','imageType', 'edition','facilityType','activation.type','foundryId','foundrySystem','img', 'formula','damage.parts','target.affects.count','system','saveDamage','attackDamage', 'definedInSource', 'displayAs','abbreviation','tokenCredit', 'credit', 'addAs','dataType','converterId']
SKIP_KEY_PATH=[
  'ability/choose/from', 
  'toolProficiencies/choose/from',
  'entries/entries/tag',
  'entries/entries/prop',
  '_copy/_mod/variant',
  'effects/changes/key',
  'effects/changes/value',
  'effects/changes/mode',
  # class/foundry.json
  'consumption/targets/value',
  'consumption/targets/target',
  'consumption/scaling/max',
  'system/uses.max',
  'activities/duration/value',
  'activities/target/template/size',
  'activities/uses/max',
  'activities/bonuses',
  'entryData/resources/count',
  'target/affects/count',
  # spells/foundry.json
  'activities/profiles/count'
  'facility/prerequisite/spellcastingFocus'
  ]
SKIP_ITEMS = [{'key':'action','value':'remove'}, {'key':'action','value':'insert'}]
# SKIP_FILES = ['book/book-phb.json', 'bestiary/bestiary-mm.json']
SKIP_DIRS = ['generated']
# SKIP_FILES = []
SKIP_FILES = ['book/book-phb.json']
RETRY_TIMES=2
DEBUG_MODE = False

KEY_MATCHED_TAG={'gear':'item', 'baseItem':'item'}

PROMOT = """
- Role: Dungeons & Dragons (D&D) 5th Edition (5e) 专家和JSON数据处理专家
- Background: 用户需要将Dungeons & Dragons 5th Edition (D&D 5e) 的英文JSON数据文件或list格式的数据文件翻译成简体中文，以便于中文用户在本地化应用中使用。
- Profile: 你是一位精通技术文档翻译的专家，具有丰富的JSON文件和list格式数据文件处理经验，擅长将游戏数据准确无误地转换为不同语言，同时保持数据结构的完整性。
- Skills: 技术文档翻译、JSON文件编辑、数据结构理解、游戏术语翻译。
- Goals: 设计一个流程，将D&D 5e的英文JSON数据文件或list格式的数据文件准确、高效地翻译成简体中文，并保持相同的数据格式。
- Constrains: 翻译应保持数据的准确性和完整性，避免数据结构的破坏，确保JSON文件在翻译后仍可正常使用。
- OutputFormat: 保持原有的JSON文件或List文件的格式，所有文本内容翻译为简体中文。只输出json或list，不需要输出其他的说明内容。注意json中不要使用中文的引号“”，而是用英文引号""
- Workflow:
  1. 分析JSON文件或list文件的结构和数据类型。
  2. 确定游戏专业术语和描述性文本的准确中文翻译。
  3. 使用专业的JSON编辑工具或list编辑工具进行翻译和数据维护。
  4. 校对和测试，确保翻译后的JSON文件或list文件在应用中能够正确加载和显示。
- Examples:
  英文原文：{"trans_str":["A fiery burst erupts from the point of impact."]}
  中文翻译：{"trans_str":[一个炽热的爆裂从冲击点爆发出来。"]}
  英文原文：{"trans_str":["druid"]}
  中文翻译：{"trans_str":["德鲁伊"]}
- Initialization: 欢迎使用专业的D&D 5e JSON数据文件翻译服务。请提供您需要翻译的英文JSON文件，我们将为您提供精确且格式一致的简体中文JSON文件翻译。
"""

SIMPLE_PROMOT = """
- Role:D&D 5e 与 JSON 数据处理专家
- Background: 用户需把 D&D 5e 英文 JSON/list 数据文件转简体中文用于本地化。
- Goals: 高效准确翻译并保留原格式。
- Constrains:保证数据准确完整，JSON 文件可用。
- OutputFormat: 维持原 JSON/list 格式，只输出翻译后数据，json 用英文引号。
- Workflow:
分析文件结构和数据类型。
明确术语与描述的中文译法。
用工具翻译并维护数据。
保留{@aaa bbb}格式的文本，并且翻译后的文本需要**保证所有{@aaa bbb}的顺序与英文一致**。
校对测试确保正常使用。
- Examples:
  英文原文：{"trans_str":["It expands on what's written about the {@book Astral Plane|DMG|2} {@b} in the {@book Dungeon Master's Guide|DMG}"]}
  中文翻译：{"trans_str":["它扩展了关于{@book 星界|DMG|2}{@b}（选自{@book 城主指南|DMG}）的描述"]}
  英文原文：{"trans_str":["druid"]}
  中文翻译：{"trans_str":["德鲁伊"]}
"""

PROMOT_KNOWLEDGE = """
- Role:D&D 5e 与 JSON 数据处理专家
- Background: 用户需把 D&D 5e 英文Json数据转为特定格式的简体中文用于本地化。
- Goals: 根据参考资料高效准确翻译并保留原格式。
- Constrains:保证数据准确完整，JSON 文件可用。
- OutputFormat: 维持原 JSON 格式，只输出翻译后数据，json 用英文引号。
- Workflow:
1.读取reference字段（相关术语，部分术语可能不符合当前语境，需结合语境来进行翻译）
2.读取parents字段（当前trans_str翻译文本的父层级，用于上下文理解）
3.分析文件结构和数据类型。
4.基于reference字段的术语和parents字段的上下文，用工具翻译并维护数据。
6.保留{@aaa bbb}格式的文本，并且翻译后的文本需要**保证所有{@aaa bbb}的顺序与英文一致**。
7.检查是否符合Json格式、{@aaa bbb}的**数量**、**内容**和**顺序**是否一致
8.输出翻译后的Json数据
- Examples:
  输入：{
    "parents":[("creature":"生物","Sul Khatesh","苏·卡特什")],
    "refrence":["苏·卡特什向一个她60尺内能看见的生物低声说出一个魔法秘密。目标必须成功通过DC 26的感知豁免否则消耗自身一个3环或更低的法术位对自己30尺内每个生物造成26（4d12）力场伤害。","Sul Khatesh:['苏·卡特什'],"Wisdom:['感知']","Force:['力场']","Stunned:['震慑']"],
    "trans_str":"Sul Khatesh whispers an arcane secret into the mind of a creature she can see within 60 feet of her. The target must succeed on a {@dc 26} Wisdom saving throw or expend one of its spell slots of 3rd level or lower and deal 26 ({@damage 4d12}) force damage to each creature within 30 feet of it. "
    }
  输出：{"trans_str":"苏·卡特什向一个她60尺内能看见的生物低声说出一个魔法秘密。目标必须成功通过{@dc 26}的感知豁免否则消耗自身一个3环或更低的法术位对自己30尺内每个生物造成26（{@damage 4d12}）力场伤害。"}
  输入：{
    "parents":[("creature":"生物"),("Sul Khatesh","苏·卡特什")],
    "refrence":["Maddening Secret": "疯狂诡秘"],
    "trans_str":"Maddening Secrets (Costs 3 Actions)"
    }
  输出：{"trans_str":"疯狂诡秘（消耗3个动作）"}
"""

PROMOT_SPELL_XPHB = """
- Role:D&D 5e 与 JSON 数据处理专家
- Background: 用户需把 D&D 5e 英文Json数据转为特定格式的简体中文用于本地化。
- Goals: 根据参考资料高效准确翻译并保留原格式。
- Constrains:保证数据准确完整，JSON 文件可用。
- OutputFormat: 维持原 JSON 格式，只输出翻译后数据，json 用英文引号。
- Workflow:
1.读取reference字段：相关中文译文
2.读取parents字段（当前trans_str翻译文本的父层级，用于上下文理解）
3.分析文件结构和数据类型。
4.基于reference字段的译文，找到trans_str字段的英文对应的译文，并将其按照英文的格式转换。
6.保留{@aaa bbb}格式的文本，并且翻译后的文本需要**保证所有{@aaa bbb}的顺序与英文一致**。
7.检查是否符合Json格式、{@aaa bbb}数量和顺序是否一致
8.输出翻译后的Json数据
- Examples:
  输入：{
    "parents":[("creature":"生物","Sul Khatesh","苏·卡特什")],
    "refrence":"造物术\nCreation\n五环 幻术（术士、法师）\n施法时间：1分钟\n施法距离：30尺\n法术成分：V、S、M（一支画笔）\n持续时间：特殊\n你从堕影冥界Shadowfell取来一些暗影物质，在施法距离内创造一个物件。你可以创造一个植物质（类似纺织品、绳索、木质等）物件，也可以创造一个矿物质（类似石质、水晶、金属等）物件。创造出来的物件大小必须不超过5尺立方区域，且其必须是一种你见过的形态与材质。\n法术的持续时间由所创造物件的材质决定，如材质表中所示。如果所创造物件由多种材质组合而成，则其持续时间取其中最短者。施展其他法术时，如果以这些创造物作为其材料成分将会使那道法术失败。\n材质Materials材质持续时间植物24小时岩石或水晶12小时贵金属1小时宝石10分钟精金或秘银1分钟\n升环施法。使用的法术位每比五环高一环，此法术的立方区域边长就增加5尺。\n\n"
    "trans_str":"The {@variantrule Cube [Area of Effect]|XPHB|Cube} increases by 5 feet for each spell slot level above 5."
    }
  输出：{"trans_str":"使用的法术位每比五环高一环，此法术的{@variantrule Cube [Area of Effect]|XPHB|立方}区域边长就增加5尺。"}
"""
PROMOT_BESTIARY_XMM = """
- Role:D&D 5e 与 JSON 数据处理专家
- Background: 用户需把 D&D 5e 英文Json数据转为特定格式的简体中文用于本地化。
- Goals: 根据参考资料高效准确翻译并保留原格式。
- Constrains:保证数据准确完整，JSON 文件可用。
- OutputFormat: 维持原 JSON 格式，只输出翻译后数据，json 用英文引号。
- Workflow:
1.读取reference字段：相关中文译文
2.读取parents字段（当前trans_str翻译文本的父层级，用于上下文理解）
3.分析文件结构和数据类型。
4.基于reference字段的译文，找到trans_str字段的英文对应的译文，并将其按照英文的格式转换。
6.保留{@aaa bbb}格式的文本，并且翻译后的文本需要**保证所有{@aaa bbb}的顺序与英文一致**。
7.检查是否符合Json格式、{@aaa bbb}数量和顺序是否一致
8.输出翻译后的Json数据
- Examples:
  输入：{
    "parents": [["Yuan-ti Abomination", "憎恶蛇人"], ["Poison Spray {@recharge 5}", "毒气喷涌{@recharge 5}"]], 
    "reference": ["憎恶蛇人\nYuan-ti Abomination\n 憎恶蛇人几乎将自身所有的人性痕迹尽数交换，逐步蜕化为带有鳞覆手臂的巨型直立蛇怪。在战斗中，它们会用其强劲的卷缚或毒牙的猛袭抓住每一个将敌人碾碎的机会。这些憎恶蛇人同样可以变形为蛇。在这种形态下的憎恶蛇人和看起来普通的大蛇类别无二致。\n憎恶蛇人的真正威胁并非源自肉体之力，而是其狡诈的头脑。这些谋略大师往往领导着其他蛇人的邪教团，并驱使它们实施那些精心酝酿的阴谋。憎恶蛇人惯于避开危险，它们通常藏身于隐秘据点之中，在蛇人们与蛇类看守的庇护下操控全局。这些冷血领袖不仅对那些为蛇人赋能的超自然力量有着独到的见解，还会时常设下一些任由它们支配的阴险魔法陷阱与突发状况。\n憎恶蛇人Yuan-ti Abomination\n大型怪兽，中立邪恶AC 15先攻 +6（16）HP 127（15d10+45）速度 40尺，攀爬30尺调整豁免调整豁免调整豁免力量19+4+4敏捷16+3+3体质17+3+3智力17+3+3感知18+4+4魅力15+2+2技能 察觉+7，隐匿+6免疫 毒素；中毒感官 黑暗视觉60尺；被动察觉17语言 深渊语，通用语，龙语CR 7（XP2900；PB+3）\n特质Traits\n魔法抗性Magic Resistance。蛇人对抗法术和其他魔法效应时进行的豁免检定具有优势。\n动作Actions\n多重攻击Multiattack。蛇人发动两次啃咬攻击，并使用施法施展暗示术Suggestion（若条件允许）。\n啃咬Bite。近战攻击检定：+7，触及5尺。命中：11（2d6+4）穿刺伤害加10（3d6）毒素伤害。\n绞缠Constrict。力量豁免检定：DC15，单一5尺内不超过大型的生物。失败：28（7d6+4）钝击伤害。目标陷入受擒状态（逃脱DC14），且目标陷入束缚状态直至擒抱结束。成功：仅半伤。\n毒气喷涌Poison Spray（充能5~6）。体质豁免检定：DC14，30尺锥状区域内的每名生物。失败：21（6d6）毒素伤害，且目标陷入中毒状态直至蛇人的下个回合结束。中毒期间，目标陷入目盲状态。成功：仅半伤。\n施法Spellcasting（仅蛇人形态）。该人施展以下一道法术，无需材料成分并使用感知作为施法属性（法术豁免DC15）：\n随意：化兽为友Animal Friendship（仅蛇）\n每项3/日：暗示术Suggestion\n附赠动作Bonus Actions\n变形Shape-Shift。蛇人变形为大型的蛇，或变回其真实形态。若其死亡，则其保持在当前的形态不变。除注明部分外，其各形态下游戏数据均相同。蛇人着装或携带的任何装备都不会随之变化。\n"], 
    "trans_str": "{@actSave con} {@dc 14}, each creature in a 30-foot {@variantrule Cone [Area of Effect]|XPHB|Cone}. {@actSaveFail} 21 ({@damage 6d6}) Poison damage, and the target has the {@condition Poisoned|XPHB} condition until the end of the yuan-ti's next turn. While {@condition Poisoned|XPHB}, the target has the {@condition Blinded|XPHB} condition. {@actSaveSuccess} Half damage only."}
  输出：{"trans_str":"{@actSave con} {@dc 14}，30尺{@variantrule Cone [Area of Effect]|XPHB|Cone}区域内的每名生物。{@actSaveFail} 21（{@damage 6d6}）毒素伤害，且目标陷入{@condition Poisoned|XPHB}状态直至蛇人的下个回合结束。{@condition Poisoned|XPHB}期间，目标陷入{@condition Blinded|XPHB|目盲}状态。{@actSaveSuccess} 仅半伤。"}
"""

PROMOT_DIFF= """
- Role: Dungeons & Dragons (D&D) 5th Edition (5e) 专家和数据分析师
- Background: 用户需要从Dungeons & Dragons 5th Edition (D&D 5e) 的两组词中找出不同的英文词，这涉及到数据比较和识别。
- Profile: 你是一位专业的数据分析师，擅长使用各种工具和方法来比较和分析数据。
- Skills: 数据比较、识别差异、逻辑分析。
- Goals: 你的目标是准确地找出两组词中不同的英文单词。
- Constrains: 需要确保比较过程中不遗漏任何单词，并且正确区分中英文单词。
- OutputFormat: 列出所有不同的英文单词。
- Workflow:
  1. 输入两组词（英文词和中文词）。
  2. 比较两组词中的英文单词。
  3. 输出不同的英文单词列表。
- Examples:
  英文词：Activate an Item,Attack,Cast a Spell,
  中文词：攻击,
  输出：Activate an Item,Attack,Cast a Spell,
- Initialization: 请输入一组英文词和一组中文词，我将找出它们中不同的英文词。
"""

REPLACE_PREFIX='need-translate-'
SUBJOB_PATTERN = r"{@[^ \}]+ ([^\}\{@}]+)\}"
ONLY_SUBJOB_PATTERN = r"^{@[^ \}]+ ([^\}\{@}]+)\}$"
TAG_PATTERN = r"{@([^ \}]+) [^\}\{@}]+\}"


# ===== 不全书相关配置 ======
CHM_ROOT_DIR = os.getenv("CHM_ROOT_DIR")
# 怪物图鉴翻译文件对照字典
BESTIARY_FILE_MAP = {
    'bestiary/bestiary-xmm.json': '怪物图鉴2025',
    'bestiary/bestiary-idrotf.json': '模组/冰风谷/生物',
    'bestiary/bestiary-skt.json': '模组/风暴君王之雷霆/图鉴'
}


# ===== 外部Core相关配置 ======
OUTPUT_DATA_DIR = "/data/pttsw-core/output"

SPLITED_5ETOOLS_DATA_DIR = EN_PATH
SPLITED_5ETOOLS_DATA_DIR = OUTPUT_DATA_DIR + "/split-data"
COMBINE_INFO_DATA_DIR = OUTPUT_DATA_DIR + "/combine-info"
COMBINED_5ETOOLS_DATA_DIR = OUTPUT_DATA_DIR + "/combined-data"
