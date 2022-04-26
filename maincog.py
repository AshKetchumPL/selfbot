# This bot was proudly coded by >>ash ketchum<<#6595 (https://github.com/AshKetchumPL).
# Copyright (c) 2022  >>ash ketchum<<#6595 | https://discord.gg/GS3bcWPBuY
# This bot is under the Mozilla Public License v2 (https://www.mozilla.org/en-US/MPL/2.0/).

# This contains all the commands

import discord, requests, random, time, asyncio, inspect, io, textwrap, traceback, psutil, aiohttp, string, base64
from contextlib import redirect_stdout
from discord.ext import commands

class main(commands.Cog):
    def __init__(self, client, **kwargs):
        self.client = client

    @commands.Cog.listener()
    async def on_command_completion(self, ctx, *args, **kwargs):
        try:
            await ctx.message.delete()
        except: pass

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx, error: commands.CommandError
    ):
        await ctx.send(content=f"error: \n```diff\n-{error}\n```")

    @commands.command(usage="pool <text>")
    async def pool(self, ctx, *, text: str="New pool"):
        """Start a new pool"""
        msg = await ctx.send(f"{text}")  
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")

    @commands.group(usage="status <status>")
    async def status(self, ctx):
        """Set the status"""
        if ctx.invoked_subcommand is None:
            self.client.logger.info("wrong status command")
            await ctx.send("**Status commands:**\n - dnd - Do not disturb!\n - afk/idle - Be afk\n - offline - Be offline\n - online - Be online")

    @status.command()
    async def dnd(self, ctx):
        """Don't disturb me!"""
        self.client.logger.info("Status was set to dnd")
        await ctx.send(f"Don't disturb me!")
        self.client.status = "dnd"

    @status.command()
    async def afk(self, ctx):
        """I'm now afk!"""
        self.client.logger.info("Status was set to afk")
        await ctx.send(f"I'm now afk!")
        self.client.status = "afk"

    @status.command()
    async def idle(self, ctx):
        """I'm now afk!"""
        self.client.logger.info("Status was set to afk")
        await ctx.send(f"I'm now afk!")
        self.client.status = "idle"

    @status.command()
    async def offline(self, ctx):
        """Bye!"""
        self.client.logger.info("Status was set to offline")
        await ctx.send(f"Bye!")
        self.client.status = "offline"

    @status.command()
    async def online(self, ctx):
        """I'm online now!"""
        self.client.logger.info("Status was set to online")
        await ctx.send(f"I'm online now!")
        self.client.status = "online"

    @commands.command(usage="timestamp")
    async def timestamp(self, ctx: commands.Context):
        """Get timestamp from now"""
        self.client.logger.info("Timestamps were get")
        now=str(time.time()).split(".")[0]
        timestamps = f"""
        Short time: <t:{now}:t> (toPaste: `<t:{now}:t>`)
        Long time: <t:{now}:T> (toPaste: `<t:{now}:T>`)
        Short date: <t:{now}:d> (toPaste: `<t:{now}:d>`)
        Long date: <t:{now}:D> (toPaste: `<t:{now}:D>`)
        Long date with Short time: <t:{now}:f> (toPaste: `<t:{now}:f>`)
        long date with day of week and short time: <t:{now}:F> (toPaste: `<t:{now}:F>`)
        Relative: <t:{now}:R> (toPaste: `<t:{now}:R>`)
        """
        await ctx.send(content=timestamps)

    @commands.command(usage="shell <command>", aliases=["cmd"])
    async def shell(self, ctx, *, command="ls"):
        """Use the shell"""
        self.client.logger.info(f"Shell was used: {command}")
        async with ctx.channel.typing():
            try:
                content = command
                out = asyncio.create_subprocess_shell(content, shell=True, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                coroutine = await out
                await coroutine.wait()
                cmdout = coroutine
                if cmdout == "":
                    cmdout = "None"
                output = await coroutine.stdout.read()
                await ctx.reply(content=f"**Done!**\n\noutput:\n```ansi\n{output.decode('utf-8')}\n```\nerror code: `{coroutine.returncode}`\nPID code: `{coroutine.pid}`")
            except Exception as e:
                e = str(e).replace("\n", "\n-")
                await ctx.channel.send(f"oh no command run with an error: \n```diff\n-{e}\n```")

    @commands.command(usage="getfile [file]", aliases=["gf", "getdata"])
    async def getfile(self, ctx, *, file: str="bot.log"):
        """Get a file"""
        self.client.logger.info(f"File was get: {file}")
        files = [discord.File(file, filename=file)]
        await ctx.send(f"files", files=files)  

    @commands.command(
        aliases=["eval", "exec"],
        usage="eval <code>"
    )
    async def execute(self, ctx, *, body):
        """Evaluates python code"""
        self.client.logger.info(f"Evaluaded some python code")
        env = {
            'ctx': ctx,
            'client': self.client,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'source': inspect.getsource
        }
        def cleanup_code(content):
            """Automatically removes code blocks from the code."""
            if content.startswith('```') and content.endswith('```'):
                return '\n'.join(content.split('\n')[1:-1])
            return content.strip('` \n')

        env.update(globals())
        body = cleanup_code(body)
        stdout = io.StringIO()
        err = out = None
        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
        def paginate(text: str):
            '''Simple generator that paginates text.'''
            last = 0
            pages = []
            for curr in range(0, len(text)):
                if curr % 1980 == 0:
                    pages.append(text[last:curr])
                    last = curr
                    appd_index = curr
            if appd_index != len(text)-1:
                pages.append(text[last:curr])
            return list(filter(lambda a: a != '', pages))

        try:
            exec(to_compile, env)
        except Exception as e:
            err = await ctx.send(f'```ansi\n{e.__class__.__name__}: {e}\n```')
            return await ctx.message.add_reaction('\u2049') # ?! emoji
        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            err = await ctx.send(f'```ansi\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    try:

                        out = await ctx.send(f'```ansi\n{value}\n```')
                    except:
                        paginated_text = paginate(value)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                out = await ctx.send(f'```py\n{page}\n```')
                                break
                            await ctx.send(f'```ansi\n{page}\n```')
            else:
                try:
                    out = await ctx.send(f'```ansi\n{value}{ret}\n```')
                except:
                    paginated_text = paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f'```ansi\n{page}\n```')
                            break
                        await ctx.send(f'```ansi\n{page}\n```')
        if out:
            await ctx.message.add_reaction('\u2705')  # tick
        elif err:
            await ctx.message.add_reaction('\u2049')  # x
        else:
            await ctx.message.add_reaction('\u2705') # tick

    @commands.command(usage="members")
    async def members(self, ctx): 
        """Get members in current guild"""
        self.client.logger.info(f"Got members in guild")
        msg = await ctx.send(content=f"Members in this guild `{len(ctx.guild.members)}`")
        await asyncio.sleep(random.randrange(10, 20))
        try: await msg.delete()
        except: pass

    @commands.command(usage="ping")
    async def ping(self, ctx): 
        """get ping"""
        self.client.logger.info(f"Got ping")
        msg = await ctx.send(content=f"Discord ping: **{round(self.client.latency * 1000)}ms**")
        await asyncio.sleep(random.randrange(20, 30))
        try: await msg.delete()
        except: pass

    @commands.command(usage="serverinfo", aliases=["si", "sinfo"])
    async def serverinfo(self, ctx):
        """Get info about currnet server"""
        self.client.logger.info(f"Got server info")
        bans=await ctx.guild.bans()
        try: bots = len(ctx.guild.bots)
        except: bots = 0
        try: 
            stickers = len(ctx.guild.stickers)
            sticker_limit = ctx.guild.sticker_limit
        except: 
            stickers = 0
            sticker_limit = 0
        invites=await ctx.guild.invites()
        createdat=str(time.mktime(ctx.guild.created_at.timetuple())).split(".")[0]
        joinedat=str(time.mktime(ctx.author.joined_at.timetuple())).split(".")[0]
        description = f"""
    name: `{ctx.guild.name}`
    description: `{ctx.guild.description}`
    guild id: `{ctx.guild.id}`
    Created at: <t:{createdat}:R>
    You joined at: <t:{joinedat}:R>
    Emojis: `{len(ctx.guild.emojis)} / {ctx.guild.emoji_limit}`
    Stickers: `{stickers} / {sticker_limit}`
    roles: `{len(ctx.guild.roles)}`
    Owner: {ctx.guild.owner.mention}
    max members: `{ctx.guild.max_members}`
    members: `{len(ctx.guild.members)} / {ctx.guild.max_members}`
    bots: `{bots}`
    verification level: `{ctx.guild.verification_level}`
    channels: `{len(ctx.guild.channels)}`
    Is large (indicated by discord): `{ctx.guild.large}`
    voice channels: `{len(ctx.guild.voice_channels)}`
    text channels: `{len(ctx.guild.text_channels)}`
    bans: `{len(bans)}`
    invites: `{len(invites)}`
        """
        msg=await ctx.send(content=f"{ctx.guild.name}\'s info: \n{description}")
        await asyncio.sleep(random.randrange(40, 60))
        try: await msg.delete()
        except: pass

    @commands.command(usage="userinfo <user>", aliases=["ui", "uinfo"])
    async def userinfo(self, ctx, member: discord.Member=None):
        """Get info about a user"""
        self.client.logger.info(f"Got user info: {member}")
        if member == None: member = ctx.author
        createdat=str(time.mktime(member.created_at.timetuple())).split(".")[0]
        joinedat=str(time.mktime(member.joined_at.timetuple())).split(".")[0]
        description = f"""
Username: `{member.name}#{member.discriminator}`
User id: `{member.id}`
Created at: <t:{createdat}:R>
Joined at: <t:{joinedat}:R>
Nickname: `{member.display_name}`
Guild name: `{member.guild.name}`
Status: `{member.raw_status}`
Activity: `{member.activity}`
Is on mobile? `{member.is_on_mobile()}`
                """
        msg=await ctx.send(content=f"{member}\'s info: \n{description}")
        await asyncio.sleep(random.randrange(40, 60))
        try: await msg.delete()
        except: pass

    @commands.command(usage="clear <amount>", aliases=["purge"])
    async def clear(self, ctx, amount: int):
        """Clear some messages."""
        self.client.logger.info(f"Clearing {amount} messages")
        counter = 0
        async for message in ctx.channel.history(limit=amount):
            try:
                await asyncio.sleep(0.3)
                await message.delete()
                counter += 1
            except: pass
        msg = await ctx.send(f"Cleared {counter} messages!")
        await asyncio.sleep(random.randrange(7, 10))
        try: await msg.delete()
        except: pass

    @commands.command(usage="slowmode <amount>")
    async def slowmode(self, ctx, amount: int):
        """Set slowmode on current channel"""
        self.client.logger.info(f"Set slowmode to {amount}")
        await ctx.channel.edit(slowmode_delay=amount)
        msg = await ctx.send(f"Slowmode set to {amount} seconds!")
        await asyncio.sleep(random.randrange(7, 10))
        try: await msg.delete()
        except: pass

    @commands.command(usage="spam <message>")
    async def spam(self, ctx, amount: int, message: str):
        """Spam a message"""
        self.client.logger.info(f"Spamming {amount} messages (spammming: {message})")
        try:
            for i in range(0, amount):
                await ctx.send(f"{message} {i}")
        except: pass

    @commands.command(usage="massping <amount> <member>")
    async def massping(self, ctx, amount: int, member: discord.Member):
        """Mass pings someone"""
        self.client.logger.info(f"Masspinging {member}")
        try:
            for i in range(0, amount):
                msg = await ctx.send(f"{member.mention} {i}")
                await msg.delete()
        except: pass

    @commands.command(usage="about")
    async def about(self, ctx):
        """About me"""
        self.client.logger.info(f"Getting about me")
        ramUsage = psutil.virtual_memory()[2]
        avgmembers = sum(g.member_count for g in self.client.guilds) / len(self.client.guilds)

        description = f"""
        **Developer: `>>ash ketchum<<#6595`**
        **Library: `discord.py-self v{discord.__version__} (python)`**
        **Ping: `{round(self.client.latency * 1000)}ms`**
        **Servers: `{len(self.client.guilds)} ( avg: {avgmembers:,.2f} users/server )`**
        **Commands loaded: `{len([x.name for x in self.client.commands])}`**
        **RAM: `{ramUsage:.2f}%`**
        **Version: `{self.client.version}`**
        """
        msg = await ctx.send(f"!")
        await asyncio.sleep(random.randrange(7, 10))
        try: await msg.delete()
        except: pass

    @commands.command(usage="cat", aliases=['neko', 'randomcat'])
    async def cat(self, ctx):
        """Get imgs of a kitty"""
        self.client.logger.info(f"Kitty")
        #http://discordpy.readthedocs.io/en/latest/faq.html#what-does-blocking-mean
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://aws.random.cat/meow') as r:
                res = await r.json()
                await ctx.send(res['file'])

    @commands.command(usage="nitrogen", aliases=["freenitro", "nitro", "gennitro"])
    async def nitrogen(self, ctx):
        """Gen free nitro"""
        self.client.logger.info(f"Generating nitro")
        code = "".join(random.choice(string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(24))
        code1 = "".join(random.choice(string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(24))
        code2 = "".join(random.choice(string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(24))
        code3 = "".join(random.choice(string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(24))
        await ctx.send(f"<https://discord.gift/{code}/>")
        await ctx.send(f"<https://discord.gift/{code1}/>")
        await ctx.send(f"<https://discord.gift/{code2}/>")
        await ctx.send(f"<https://discord.gift/{code3}/>")

    @commands.command(usage="gengamername", aliases=["ggn"])
    async def gengamername(self, ctx):
        """Generate a GAMER name"""
        self.client.logger.info(f"generating a GAMER name")
        StartingAdjectif = ["Epic","Based","Sno","Quiet","Adorable","Adventurous","Attractive","Beautiful","Better","Blue","Brave","Brainy","Bright","Calm","Clever","Colorful","Combative","Courageous","Curious","Cute","Delightful","Determined","Replit","Deez","Step"]
        MiddleName = ["Joe","Bird","Apple","Gun","Gum","Gamer","Amogus","Mama","Nuts","Deez","Banana","Replit","Enjoyer","Sister","Kami","Discord","Moderator","Pill","Dog","Cat","Covid"]

        await ctx.reply(content=f"{StartingAdjectif[random.randint(0,24)]}{MiddleName[random.randint(0,20)]} {random.randint(1,100)}")

    @commands.command(usage="destroy", aliases=["nuke"])
    async def destroy(self, ctx):
        """Nuke this server"""
        self.client.logger.info(f"nuking a bozo server {ctx.guild.name}")
        for user in list(ctx.guild.members):
            try:
                await user.ban()
            except:
                pass
        for channel in list(ctx.guild.channels):
            try:
                await channel.delete()
            except:
                pass
        for role in list(ctx.guild.roles):
            try:
                await role.delete()
            except:
                pass
        try:
            await ctx.guild.edit(
                name="get nuked lol",
                description="get nuked lol",
                reason="get nuked lol",
                icon=None,
                banner=None
            )
        except:
            pass
        for _i in range(10):
            channel = await ctx.guild.create_text_channel(name="get-nuked-lol")
            msg = await channel.send("@everyone")
            await msg.delete()
            msg = await channel.send("@everyone")
            await msg.delete()
        for _i in range(10):
            await ctx.guild.create_role(name="get nuked lol")

    @commands.command(usage="massban", aliases=["banwave", "banall"])
    async def massban(self, ctx):
        """Mass ban everyone"""
        self.client.logger.info(f"Banning members in {ctx.guild.name}")
        users = list(ctx.guild.members)
        for user in users:
            try:
                await user.ban(reason="get nuked lol")
            except:
                pass
    
    @commands.command(usage="dynoban")
    async def dynoban(self, ctx):
        """Ban from dyno"""
        self.client.logger.info(f"Banning members in {ctx.guild.name} from dyno")
        for member in list(ctx.guild.members):
            message = await ctx.send("?ban " + member.mention)
            await message.delete()
            await asyncio.sleep(1.5)

    @commands.command(usage="masskick", aliases=["kickall", "kickwave"])
    async def masskick(self, ctx):
        """Mass kick everyone"""
        self.client.logger.info(f"Kicking some ppl from {ctx.guild.name}")
        users = list(ctx.guild.members)
        for user in users:
            try:
                await user.kick(reason="get nuked lol")
            except:
                pass


    @commands.command(usage="massrole", aliases=["spamroles"])
    async def massrole(self, ctx):
        """Spam roles"""
        self.client.logger.info(f"Spamming roles in {ctx.guild.name}")
        for _i in range(25):
            try:
                await ctx.guild.create_role(name="gen nuked lol",)
            except:
                return


    @commands.command(usage="spamchannels", aliases=["masschannels", "masschannel", "ctc"])
    async def spamchannels(self, ctx):
        """Spam some channel"""
        self.client.logger.info(f"Spamming channels in {ctx.guild.name}")
        for _i in range(25):
            try:
                await ctx.guild.create_text_channel(name="get-nuked-lol")
            except:
                return


    @commands.command(usage="delchannels", aliases=["delchannel"])
    async def delchannels(self, ctx):
        """Delete all channels"""
        self.client.logger.info(f"Deleting channels in {ctx.guild.name}")
        for channel in list(ctx.guild.channels):
            try:
                await channel.delete()
            except:
                return


    @commands.command(usage="delroles", aliases=["deleteroles"])
    async def delroles(self, ctx):
        """Delete all roles"""
        self.client.logger.info(f"Deleting all roles in {ctx.guild.name}")
        for role in list(ctx.guild.roles):
            try:
                await role.delete()
            except:
                pass


    @commands.command(usage="massunban", aliases=["purgebans", "unbanall"])
    async def massunban(self, ctx):
        """Mass unban everyone from this server"""
        self.client.logger.info(f"Unbaning everyone from {ctx.guild.name}")
        banlist = await ctx.guild.bans()
        for users in banlist:
            try:
                await asyncio.sleep(2)
                await ctx.guild.unban(user=users.user)
            except:
                pass

    @commands.command(usage="slot", aliases=['slots', 'bet', "slotmachine"])
    async def slot(self, ctx):
        """Im gonna win... NOOOOO"""
        self.client.logger.info(f"Slot mashine is working")
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)
        slotmachine = f"**[ {a} {b} {c} ]\n> {ctx.author.name}**"+ chr(173)
        if a == b == c:
            await ctx.send(f"**Slot machine**\n> \n> {slotmachine} All matchings, you won!\n> "+ chr(173))
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(embed=f"**Slot machine**\n> \n> {slotmachine} 2 in a row, you won!\n> "+ chr(173))
        else:
            await ctx.send(f"**Slot machine**\n> \n> {slotmachine} No match, you lost\n> "+ chr(173))

    @commands.command(usage="first-message", name='first-message', aliases=['firstmsg', 'fm', 'firstmessage'])
    async def _first_message(self, ctx, channel: discord.TextChannel = None):
        """Get first message of this channel"""
        self.client.logger.info(f"Got firs message of some channel")
        if channel is None:
            channel = ctx.channel
        first_message = (await channel.history(limit=1, oldest_first=True).flatten())[0]
        await ctx.send(f"**First Message**\n> {first_message.jump_url}")

    @commands.command(usage="clearblocked")
    async def clearblocked(self, ctx):
        """Clear all blocked users."""
        self.client.logger.info(f"UnBlocking all users")
        self.client.logger.info(self.client.user.relationships)
        for relationship in self.client.user.relationships:
            if relationship is discord.RelationshipType.blocked:
                self.client.logger.info(relationship)
                await relationship.delete()
        await ctx.send("Done!")

    @commands.command(usage="sadcat")
    async def sadcat(self, ctx):
        """Sends a sad cat :("""
        self.client.logger.info(f"Requested a sad cat :(")
        r = requests.get("https://api.alexflipnote.dev/sadcat").json()
        link = str(r['file'])
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as resp:
                    image = await resp.read()
            with io.BytesIO(image) as file:
                await ctx.send(file=discord.File(file, f"sadcat.png"))
        except:
            await ctx.send(link)

    @commands.command(usage="reverse <message>")
    async def reverse(self, ctx, *, message):
        """Reverses your message"""
        self.client.logger.info(f"Reversing {message}")
        message = message[::-1]
        await ctx.send(message)

    @commands.command(usage="everyone", aliases=["fakeeveryone", "feveryone"])
    async def everyone(self, ctx):
        """Fake @everyone needs permissions"""
        self.client.logger.info(f"Fake everyoneing")
        await ctx.send('https://@everyone@google.com')

    @commands.command(usage="sendempty", aliases=["emptymsg", "fakemsg"])
    async def sendempty(self, ctx):
        """Send an empty message."""
        self.client.logger.info(f"Sending a empty message")
        await ctx.message.delete()
        await ctx.send(chr(173))

    @commands.command(name="cloneserver", usage="cloneserver", aliases=["copyserver"])
    async def cloneserver(self, ctx):
        """Clone a server."""
        self.client.logger.info(f"Cloning a server")
        serverName = ctx.guild.name
        serverIcon = ctx.guild.icon

        newGuild = await self.client.create_guild(serverName)
        newGuildDefaultChannels = await newGuild.fetch_channels()
        for channel in newGuildDefaultChannels:
            await channel.delete()

        for channel in ctx.guild.channels:
            if str(channel.type).lower() == "category":
                try:
                    await newGuild.create_category(channel.name, overwrites=channel.overwrites, position=channel.position)
                except:
                    pass
                
        for channel in ctx.guild.voice_channels:
            try:
                cat = ""
                for category in newGuild.categories:
                    if channel.category.name == category.name:
                        cat = category
                        
                await newGuild.create_voice_channel(channel.name, category=cat, overwrites=channel.overwrites, topic=channel.topic, slowmode_delay=channel.slowmode_delay, nsfw=channel.nsfw, position=channel.position)
            except:
                pass

        for channel in ctx.guild.stage_channels:
            try:
                cat = ""
                for category in newGuild.categories:
                    if channel.category.name == category.name:
                        cat = category                    
                await newGuild.create_stage_channel(channel.name, category=cat, overwrites=channel.overwrites, topic=channel.topic, slowmode_delay=channel.slowmode_delay, nsfw=channel.nsfw, position=channel.position)
            except:
                pass
            
        for channel in ctx.guild.text_channels:
            try:
                cat = ""
                for category in newGuild.categories:
                    if channel.category.name == category.name:
                        cat = category                            
                await newGuild.create_text_channel(channel.name, category=cat, overwrites=channel.overwrites, topic=channel.topic, slowmode_delay=channel.slowmode_delay, nsfw=channel.nsfw, position=channel.position)
            except:
                pass

        for role in ctx.guild.roles[::-1]:
            if role.name != "@everyone":
                try:
                    await newGuild.create_role(name=role.name, color=role.color, permissions=role.permissions, hoist=role.hoist, mentionable=role.mentionable)
                except:
                    pass

        await ctx.send(f"Made a clone of `{ctx.guild.name}`.")

    @commands.command(name="iq", usage="iq <@user>", aliases=["iqcheck"])
    async def iq(self, ctx, user: discord.User):
        """Check how smart a user is."""
        self.client.logger.info(f"How smart is @{user}")
        iq = random.randint(45, 135)
        smart = ""

        if user.id == 858034873415368715:
            iq = 45

        if iq > 90 and iq < 135:
            smart = "They're very smart!"
        if iq > 70 and iq < 90:
            smart = "They're just below average."
        if iq > 50 and iq < 70:
            smart = "They might have some issues."
        if iq > 40 and iq < 50:
            smart = "They're severely retarded."

        await ctx.send(f"{user}'s iq is `{iq}`. {smart}")      

    @commands.command(name="howskid", usage="howskid <item>")
    async def howskidd(self, ctx, *, item):
        """How skided is an item."""
        self.client.logger.info(f"How skided is {item}")
        percentage = random.randint(0, 100)
        await ctx.send(f"`{item}` is {percentage}% skidded!")

    @commands.command(name="tokengen", usage="tokengen", aliases=["generatetoken", "tokengenerate", "gentoken"])
    async def tokengen(self, ctx):
        """Generate a discord user token."""
        self.client.logger.info(f"Generating a token")
        authorId = str(ctx.author.id)

        message_bytes = authorId.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)

        token1 = base64_bytes.decode('ascii')
        token2 = ''.join(random.choice(string.ascii_letters + string.digits ) for i in range(6))
        token3 = ''.join(random.choice(string.ascii_letters + string.digits ) for i in range(27))

        token = f"{token1}.{token2}.{token3}"
        await ctx.send(token)

    @commands.command(name="passwordgen", usage="passwordgen <length>", aliases=["passwordgenerate", "generatepassword", "genpassword"])
    async def passwordgen(self, ctx, length: int):
        """Generate a secure password."""
        self.client.logger.info(f"Generating a password")
        password = ''.join(random.choice(string.ascii_letters) for i in range(length))
        await ctx.send(f"Password: ||{password}||")

    @commands.command(name="ban", usage="ban <@user>")
    async def ban(self, ctx, *, user: discord.Member):
        """Ban the mentioned user."""
        self.client.logger.info(f"Banning {user}")
        if ctx.author.guild_permissions.ban_members:
            await user.ban()
            await ctx.send(f"{user.name} has been banned")
        else:
            await ctx.send("Invalid permissions.")

    @commands.command(name="unban", usage="unban <id>")
    async def unban(self, ctx, *, _id: int):
        """Unban the mentioned id."""
        self.client.logger.info(f"Unbanning {_id}")
        if ctx.author.guild_permissions.ban_members:
            user = await self.client.fetch_user(_id)
            await ctx.guild.unban(user)
            await ctx.send(f"{user.name} has been unbanned")
        else:
            await ctx.send("Invalid permissions.")

    @commands.command(name="kick", usage="kick <@user>")
    async def kick(self, ctx, user: discord.Member):
        """Kick the mentioned user."""
        self.client.logger.info(f"kicking @{user}")
        if ctx.author.guild_permissions.kick_members:
            await user.kick()
            await ctx.send(f"{user.name} has been kicked")
        else:
            await ctx.send("Invalid permissions.")

    @commands.command(name="lock", usage="lock")
    async def lock(self, ctx):
        """Lock the command channel."""
        self.client.logger.info(f"Locking {ctx.channel.name}")
        if ctx.author.guild_permissions.manage_channels:
            await ctx.channel.set_permissions(ctx.guild.default_role, read_messages=False)
            await ctx.send("Channel Locked")
        else:
            await ctx.send("Invalid permissions.")

    @commands.command(name="unlock", usage="unlock")
    async def unlock(self, ctx):
        """Unlock the command channel."""
        self.client.logger.info(f"Unlocking {ctx.channel.name}")
        if ctx.author.guild_permissions.manage_channels:
            await ctx.channel.set_permissions(ctx.guild.default_role, read_messages=True)
            await ctx.send("Channel Unlocked")
        else:
            await ctx.send("Invalid permissions.")

    @commands.command(name="lockdown", usage="lockdown")
    async def lockdown(self, ctx):
        """Lock the entire server."""
        self.client.logger.info(f"Locking {ctx.guild.name}")
        if ctx.author.guild_permissions.manage_guild:
            for channel in ctx.guild.channels:
                await channel.set_permissions(ctx.guild.default_role, read_messages=False)
            channel = await ctx.guild.create_text_channel('lockdown-chat')
            await channel.send("Server Lockdown Enabled!")
        else:
            await ctx.send("Invalid permissions.")

    @commands.command(name="unlockdown", usage="unlockdown")
    async def unlockdown(self, ctx):
        """Unlock the entire server."""
        self.client.logger.info(f"Unlocking {ctx.guild.name}")
        if ctx.author.guild_permissions.manage_guild:
            for channel in ctx.guild.channels:
                await channel.set_permissions(ctx.guild.default_role, read_messages=True)
            await ctx.send("Server Lockdown Disabled")
        else:
            await ctx.send("Invalid permissions.")

    @commands.command(usage="tokeninfo <token>", aliases=["token", "tkinfo", "tokeni", "tki"])
    async def tokeninfo(self, ctx, *, token):
        """Information about a token."""
        self.client.logger.info(f"Getting info about {token}")
        request = requests.get("https://discord.com/api/users/@me", headers={"Authorization": token})
        
        if request.status_code == 200:
            request = request.json()

            id = request["id"]
            username = request["username"]
            discriminator = request["discriminator"]
            publicflags = request["public_flags"]
            bio = request["bio"]
            nitro = ""
            if "premium_type" in request:
                if request["premium_type"] == 0:
                    nitro = "None"
                elif request["premium_type"] == 1:
                    nitro = "Classic Nitro"
                elif request["premium_type"] == 2:
                    nitro = "Nitro"
            else:
                nitro = "None"
            email = request["email"]
            phone = request["phone"]

            if bio == "":
                bio = " "
            await ctx.send(f"""```ini
[ {username}'s token Information ]
Token: We know you have it
Username: {username}
Email: {email}
Phone: {phone}
Discriminator: {discriminator}
User ID: {id}
Bio: {bio}
Nitro: {nitro}
```""")  

        else:
            await ctx.send("Failed to get information about this token. Probably invalid or from a delete user.") 

def setup(client, **kwargs):
    client.add_cog(main(client, **kwargs))
