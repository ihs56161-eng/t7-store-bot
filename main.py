import discord
from discord.ext import commands
from discord.ui import Select, View, Button
from flask import Flask
from threading import Thread
import os

# سيرفر الفلاسك عشان يبقى البوت صاحي 24/7 مع UptimeRobot
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

# إعداد البوت
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# ==========================================
# ⚙️ [إعدادات الرتب المحددة]
# ==========================================
ROLE_STAFF = 1525954290450043091     # رتبة الاستاف (للإستفسار والشكوى)
ROLE_SCAM = 1533127895390621866      # رتبة تشهير السراقين
# ==========================================

# ----------------- القائمة المنسدلة للتذاكر -----------------
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="استفسار", 
                description="للاستفسارات ومشاكل الحساب العامة", 
                emoji="<:emoji_14:1534202781320351994>"
            ),
            discord.SelectOption(
                label="شكوى", 
                description="لتقديم شكوى مباشرة أو مشكلة متعلقة بالحساب", 
                emoji="<a:emoji_7:1526263693615173824>"
            ),
            discord.SelectOption(
                label="تشهير سراقين", 
                description="للتشهير أو البلاغات المتعلقة بالسراقين", 
                emoji="<:emoji_3:1526260783263125635>"
            )
        ]
        super().__init__(placeholder="اختر خيار التذكرة...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="TICKETS")
        if not category:
            category = await guild.create_category("TICKETS")

        selected_value = self.values[0]
        target_role_id = None

        # ربط كل خيار بالآييدي الصحيح
        if selected_value == "استفسار":
            target_role_id = ROLE_STAFF
        elif selected_value == "شكوى":
            target_role_id = ROLE_STAFF
        elif selected_value == "تشهير سراقين":
            target_role_id = ROLE_SCAM

        # إنشاء الروم (مرئي للجميع)
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category
        )

        embed = discord.Embed(
            title="<:emoji_10:1534076771039838370> تذكرة جديدة",
            description=f"مرحباً بك {interaction.user.mention}!\nنوع التذكرة: **{selected_value}**\n\nاكتب تفاصيلك هنا.\nMaDe FoR T7 STORE .",
            color=0x9B59B6
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        view = TicketControlView()
        
        # تجهيز المنشن (صاحب التذكرة + الرتبة المخصصة للقسم)
        ping_content = f"{interaction.user.mention}"
        if target_role_id:
            role = guild.get_role(target_role_id)
            if role:
                ping_content += f" {role.mention}"

        await channel.send(content=ping_content, embed=embed, view=view)
        await interaction.response.send_message(f"✅ تم فتح تذكرتك بنجاح: {channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# ----------------- أزرار التحكم داخل التكت -----------------
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

# ----------------- أمر إرسال رسالة التذاكر الأساسية -----------------
@bot.command()
@commands.has_permissions(administrator=True)
async def setticket(ctx):
    embed = discord.Embed(
        title="<:emoji_10:1534076771039838370> مرحبًا بك في نظام التذاكر!",
        description=(
            "إذا كنت تحتاج مساعدة، أو لديك استفسار، أو تواجه مشكلة، أو ترغب بالتواصل مع الإدارة، اضغط على الزر أدناه لفتح تذكرة.\n\n"
            "يرجى:\n"
            "• شرح مشكلتك أو طلبك بوضوح.\n"
            "• عدم فتح أكثر من تذكرة لنفس السبب.\n"
            "• التحلي بالاحترام أثناء التحدث مع فريق الدعم.\n\n"
            "<a:emoji_9:1534068709541548183> سيتم الرد عليك في أقرب وقت ممكن."
        ),
        color=0x9B59B6
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    
    view = TicketView()
    await ctx.send(embed=embed, view=view)
    try:
        await ctx.message.delete()
    except:
        pass

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} - T7 STORE Bot is ready!")

# تشغيل السيرفر والبوت
keep_alive()

# سحب التوكن خفياً من متغيرات البيئة في ريندر
TOKEN = os.environ.get("TOKEN")
bot.run(TOKEN)
