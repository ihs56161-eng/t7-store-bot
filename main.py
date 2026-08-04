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
ROLE_STAFF = 1525954290450043091          # رتبة الاستاف (للإستفسار والشكوى والشراء)
ROLE_SCAM = 1533127895390621866           # رتبة تشهير السراقين
ROLE_MIDDLEMAN_1 = 1526627172276502591    # رتبة وسيط درجة أولى
ROLE_MIDDLEMAN_2 = 153420274328           # رتبة وسيط درجة ثانية
ROLE_MIDDLEMAN_3 = 1526627045247946843    # رتبة وسيط درجة ثالثة
# ==========================================

# ----------------- القائمة المنسدلة للتذاكر الرئيسية -----------------
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
                label="شراء", 
                description="هذا الخيار مخصص لشراء الأسلحة أو الحسابات", 
                emoji="<a:emoji_7:1526263667736187072>"
            ),
            discord.SelectOption(
                label="تشهير سراقين", 
                description="للتشهير أو البلاغات المتعلقة بالسراقين", 
                emoji="<:emoji_3:1526260783263125635>"
            ),
            discord.SelectOption(
                label="طلب وسيط درجة اولى", 
                description="لطلب وسيط تجاري درجة اولى", 
                emoji="<:emoji_11:1534202727880589424>"
            ),
            discord.SelectOption(
                label="طلب وسيط درجة ثانيه", 
                description="لطلب وسيط تجاري درجة ثانيه", 
                emoji="<:emoji_11:1534202743282204743>"
            ),
            discord.SelectOption(
                label="طلب وسيط درجة ثالثه", 
                description="لطلب وسيط تجاري درجة ثالثه", 
                emoji="<:emoji_12:1534202761238020106>"
            )
        ]
        super().__init__(placeholder="اختر خيار التذكرة...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        # ----------------- [التحقق من عدم وجود تذكرة مفتوحة مسبقاً] -----------------
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"❌ عذراً، لديك تذكرة مفتوحة بالفعل ولا يمكنك فتح أكثر من تذكرة: {existing_channel.mention}", ephemeral=True)
            return

        category = discord.utils.get(guild.categories, name="TICKETS")
        if not category:
            category = await guild.create_category("TICKETS")

        selected_value = self.values[0]
        
        # تحديد الرتبة المستجيبة حسب الخيار
        target_role_id = ROLE_STAFF
        if selected_value == "تشهير سراقين":
            target_role_id = ROLE_SCAM
        elif selected_value == "طلب وسيط درجة اولى":
            target_role_id = ROLE_MIDDLEMAN_1
        elif selected_value == "طلب وسيط درجة ثانيه":
            target_role_id = ROLE_MIDDLEMAN_2
        elif selected_value == "طلب وسيط درجة ثالثه":
            target_role_id = ROLE_MIDDLEMAN_3

        # إنشاء الروم (مرئي للجميع)
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category
        )

        embed = discord.Embed(
            title="<:emoji_10:1534076771039838370> تذكرة جديدة",
            description=f"مرحباً بك {user.mention}!\nنوع التذكرة: **{selected_value}**\n\nاكتب تفاصيلك هنا.\nسيقوم المختص بالرد عليك قريباً.\nMaDe FoR T7 STORE .",
            color=0x9B59B6
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        view = StaffControlView()
        
        ping_content = f"{user.mention}"
        role = guild.get_role(target_role_id)
        if role:
            ping_content += f" {role.mention}"

        await channel.send(content=ping_content, embed=embed, view=view)
        await interaction.response.send_message(f"✅ تم فتح تذكرتك بنجاح: {channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# ----------------- أزرار التحكم الخاصة بالإستاف فقط -----------------
class StaffControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

    # التحقق من صلاحيات الإستاف أو الرتب الخاصة بالوساطة
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        allowed_roles = [ROLE_STAFF, ROLE_SCAM, ROLE_MIDDLEMAN_1, ROLE_MIDDLEMAN_2, ROLE_MIDDLEMAN_3]
        has_permission = any(role.id in allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator
        
        if not has_permission:
            await interaction.response.send_message("❌ عذراً، هذه الأزرار مخصصة للإستاف والمختصين فقط!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="استلام التكت", style=discord.ButtonStyle.success, emoji="🙋‍♂️")
    async def claim_ticket(self, interaction: discord.Interaction, button: Button):
        button.disabled = True
        button.label = f"تم الاستلام بواسطة {interaction.user.name}"
        
        self.add_item(UnclaimButton())
        await interaction.message.edit(view=self)
        await interaction.response.send_message(f"🙋‍♂️ قام الإداري {interaction.user.mention} باستلام التذكرة!")

    @discord.ui.button(label="قفل التكت", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🔒 جاري إغلاق التذكرة خلال 5 ثوانٍ...")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

# زر إلغاء الاستلام
class UnclaimButton(Button):
    def __init__(self):
        super().__init__(label="إلغاء الاستلام", style=discord.ButtonStyle.secondary, emoji="↩️")

    async def callback(self, interaction: discord.Interaction):
        for child in self.view.children:
            if child.label and "تم الاستلام" in child.label:
                child.disabled = False
                child.label = "استلام التكت"
        
        self.view.remove_item(self)
        await interaction.message.edit(view=self.view)
        await interaction.response.send_message(f"↩️ تم إلغاء استلام التذكرة بواسطة {interaction.user.mention}", ephemeral=True)

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
    
