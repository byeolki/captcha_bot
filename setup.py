from nextcord.ext import commands
import nextcord, datetime, sqlite3, pytz, random, asyncio, string, os
from nextcord import ButtonStyle, SlashOption
from nextcord.utils import get
from nextcord.ui import Button, View
from nextcord.abc import ChannelType, GuildChannel
from captcha.image import ImageCaptcha

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='접두사 입력', intents=intents)

@client.event
async def on_ready():
    i = datetime.datetime.now()
    print(f"{client.user.name}봇은 준비가 완료 되었습니다.")
    print(f"[!] 참가 중인 서버 : {len(client.guilds)}개의 서버에 참여 중")
    print(f"[!] 이용자 수 : {len(client.users)}와 함께하는 중")

@client.slash_command(name="인증추가",description="인증을 설정 하실 수 있습니다!")
async def hello(inter: nextcord.Interaction, 인증_역할: nextcord.Role = SlashOption(description = "인증 후 지급할 역할을 선택해주세요!"), 인증_메시지: str = SlashOption(description = "인증 할때 메세지를 입력해주세요!"), 인증_채널: GuildChannel = SlashOption(description = "인증할 채널을 선택해주세요!",channel_types = [ChannelType.text])) -> None:
    if inter.user.guild_permissions.administrator:
        conn = sqlite3.connect("setup.db", isolation_level=None)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS learn(channel_id INTEGER, command TEXT, role_id INTEGER)")
        image = ImageCaptcha(width = 280, height = 90)
        captcha_text = random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)
        data = image.generate()
        image.write(captcha_text, f'{captcha_text}.png')
        c.execute("INSERT INTO learn(channel_id, command, role_id) VALUES (?, ?, ?)", (인증_채널.id, 인증_메시지, 인증_역할.id,))
        embed = nextcord.Embed(title=f"인증 설정이 완료되었어요!", description=f"{인증_채널}에서 {인증_메시지}를 치면 됩니다!\n예시 이미지를 표기해 드릴게요!",\
        color=0xd8b0cc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        file =  nextcord.File(f'{captcha_text}.png')
        await inter.response.send_message(embed=embed, file=file) 
    else:
        await inter.response.send_message("관리자 권한이 필요합니다!")

@client.event
async def on_message(message):
    conn = sqlite3.connect("setup.db", isolation_level=None)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS learn(channel_id INTEGER, command TEXT, role_id INTEGER)")
    if c.execute(f"SELECT * FROM learn WHERE command=?",(message.content,)).fetchone() is not None:
        if c.execute(f"SELECT * FROM learn WHERE channel_id=?",(message.channel.id,)).fetchone() is not None:
            image = ImageCaptcha(width = 280, height = 90)
            captcha_text = random.choice(list(string.ascii_letters))+random.choice(list(string.ascii_letters))+random.choice(list(string.ascii_letters))+random.choice(list(string.ascii_letters))+random.choice(list(string.ascii_letters))
            data = image.generate(captcha_text)
            print(captcha_text)
            image.write(captcha_text, f'{captcha_text}.png')
            embed = nextcord.Embed(title=f"인증!", description=f"아래 이미지의 글씨를 적어주세요!\n제한시간 30초",\
            color=0xd8b0cc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
            embed.set_footer(text="Bot made by 시바-스튜디오", icon_url="https://cdn.discordapp.com/attachments/997811966032756778/998133087294734388/73d6085d5acbc7ac.png")
            file =  nextcord.File(f'{captcha_text}.png')
            await message.reply(embed=embed, file=file)
            os.remove(f'{captcha_text}.png')
            def check(m):
                return m.author == message.author and m.channel == message.channel
            try:
                msg = await client.wait_for("message", check=check, timeout=30)
                if msg.content.lower() == captcha_text.lower() :
                    x = c.execute(f"SELECT * FROM learn WHERE command=? AND channel_id=?",(message.content,message.channel.id,)).fetchone()
                    role = nextcord.utils.get(message.guild.roles, id=x[-1])
                    await msg.author.add_roles(role)
                    await message.reply("성공! 역할이 지급 되었어요!")
                else:
                    await message.reply("이런 아니에요!")
            except asyncio.exceptions.TimeoutError:
                await message.channel.send("시간이 초과되었습니다.")

@client.slash_command(name="인증삭제",description="인증을 설정 하실 수 있습니다!")
async def hello(inter: nextcord.Interaction, 인증_채널: GuildChannel = SlashOption(description = "인증을 삭제할 채널을 선택해주세요!",channel_types = [ChannelType.text])) -> None:
    if inter.user.guild_permissions.administrator:
        conn = sqlite3.connect("setup.db", isolation_level=None)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS learn(channel_id INTEGER, command TEXT, role_id INTEGER)")
        if c.execute(f"SELECT * FROM learn WHERE channel_id=?",(인증_채널.id,)).fetchone() is not None:
            c.execute("DELETE FROM learn WHERE channel_id=?", (인증_채널.id,))
            embed = nextcord.Embed(title=f"인증 설정이 완료되었어요!", description=f"{인증_채널.mention}의 등록된 인증이 삭제 됬어요!",\
            color=0xd8b0cc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
            embed.set_footer(text="Bot made by 시바-스튜디오", icon_url="https://cdn.discordapp.com/attachments/997811966032756778/998133087294734388/73d6085d5acbc7ac.png")
            return await inter.response.send_message(embed=embed)
        await inter.send("해당 채널에 인증이 등록 되지 않았어요!")
        
client.run('토큰 입력')
