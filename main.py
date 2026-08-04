import discord
from discord.ext import commands
from discord.ui import Select, View, Button
from flask import Flask
from threading import Thread
import os

# إعداد سيرفر الفلاسك عشان UptimeRobot يخليه صاحي 24/7
app = Flask('')

@app.route('/')
def home():
    return "T7-STORE Bot is online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# إعدادات البوت
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="استفسار عام", 
                description="للاستفسارات والأسئلة العامة", 
                emoji="<:828044ticket:1527549672175046668>"
            ),
            discord.SelectOption(
                label="شكوى / مشكلة", 
                description="لتقديم شكوى أو الإبلاغ عن مشكلة", 
                emoji="⚠️"
            ),
            discord.SelectOption(
                label="شراء / طلب", 
                description="لشراء منتج أو طلب خدمة", 
                emoji="🛒"
            )
        ]
        super().__init__(placeholder="اختر خيار التذكرة...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="TICKETS")
        if not category:
            category = await guild.create_category("TICKETS")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="<:828044ticket:1527549672175046668> تذكرة جديدة",
            description=f"مرحباً بك {interaction.user.mention}!\nنوع التذكرة: **{self.values[0]}**\n\nاكتب تفاصيلك هنا.\nMaDe FoR T7 STORE .",
            color=0x9B59B6
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

        view = TicketControlView()
        await channel.send(content=f"{interaction.user.mention} @here", embed=embed, view=view)
        await interaction.response.send_message(f"✅ تم فتح تذكرتك بنجاح: {channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="قفل التكت", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🔒 جاري إغلاق التذكرة خلال 5 ثوانٍ...")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="استلام التكت", style=discord.ButtonStyle.success, emoji="🙋‍♂️")
    async def claim_ticket(self, interaction: discord.Interaction, button: Button):
        button.disabled = True
        button.label = f"تم الاستلام بواسطة {interaction.user.name}"
        await interaction.message.edit(view=self)
        await interaction.response.send_message(f"🙋‍♂️ قام الإداري {interaction.user.mention} باستلام التذكرة!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setticket(ctx):
    embed = discord.Embed(
        title="<:828044ticket:1527549672175046668> مرحبًا بك في نظام التذاكر!",
        description=(
            "إذا كنت تحتاج مساعدة، أو لديك استفسار، أو تواجه مشكلة، أو ترغب بالتواصل مع الإدارة، اضغط على الزر أدناه لفتح تذكرة.\n\n"
            "يرجى:\n"
            "• شرح مشكلتك أو طلبك بوضوح.\n"
            "• عدم فتح أكثر من تذكرة لنفس السبب.\n"
            "• التحلي بالاحترام أثناء التحدث مع فريق الدعم.\n\n"
            "<a:emoji_9:1534068709541548183> سيتم الرد عليك في أقرب وقت ممکن."
        ),
        color=0x9B59B6
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    
    view = TicketView()
    await ctx.send(embed=embed, view=view)
    await ctx.message.delete()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} - T7 STORE Bot is ready!")

# تشغيل سيرفر الفلاسك في الخلفية أولاً
keep_alive()

# تشغيل البوت بالتوكن حقك (حط التوكن بين العلامتين)
bot.run("حط_التوكن_هنا")
