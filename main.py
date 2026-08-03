import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Select

TOKEN = "MTUzMzYxMzI3OTQ1MTI4NzU4Mw.GZZabf.QiDfBswOrK6OICdwPkUjpL5d1pzVBEfoNaT-o0"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة اختيار سبب التذكرة
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="شراء حساب", description="فتح تذكرة لشراء حساب جديد", emoji="🛒"),
            discord.SelectOption(label="مشكلة دفع", description="الإبلاغ عن مشكلة في عملية الدفع", emoji="💳"),
            discord.SelectOption(label="استرجاع", description="طلب استرجاع منتج أو خدمة", emoji="🔄"),
            discord.SelectOption(label="استفسار", description="طرح سؤال أو استفسار عام", emoji="❓"),
            discord.SelectOption(label="أخرى", description="أسباب أخرى", emoji="⚙️")
        ]
        super().__init__(placeholder="اختر سبب فتح التذكرة...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        
        if not category:
            category = await guild.create_category("Tickets")

        # التحقق من عدم وجود تذكرة مفتوحة نفس الاسم مسبقاً
        ticket_name = f"{self.values[0]}-{interaction.user.name}".lower().replace(" ", "-")
        existing_channel = discord.utils.get(category.text_channels, name=ticket_name)
        if existing_channel:
            await interaction.response.send_message("لديك تذكرة مفتوحة بالفعل مسبقاً!", ephemeral=True)
            return

        # صلاحيات الرتب الإدارية (Team Staff و New Staff)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        for role_name in ["Team Staff", "New Staff"]:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        # إنشاء روم التذكرة
        channel = await guild.create_text_channel(ticket_name, category=category, overwrites=overwrites)

        embed = discord.Embed(
            title="T7 STORE SUPPORT",
            description=f"مرحباً بك في نظام الدعم الخاص بـ **T7 STORE**.\nالسبب: **{self.values[0]}**\n\nالرجاء الانتظار قليلاً حتى ترد عليك الإدارة.",
            color=discord.Color.dark_blue()
        )
        
        await channel.send(f"{interaction.user.mention}", embed=embed, view=TicketControlsView())
        await interaction.response.send_message(f"تم إنشاء تذكرتك بنجاح: {channel.mention}", ephemeral=True)

class TicketSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# أزرار داخل التذكرة (إغلاق / استلام)
class TicketControlsView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="قفل التذكرة", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("جاري إغلاق التذكرة...")
        await interaction.channel.delete()

    @discord.ui.button(label="استلام التذكرة", style=discord.ButtonStyle.success, emoji="🙋‍♂️")
    async def claim_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(f"تم استلام التذكرة بواسطة الإداري: {interaction.user.mention}")

# أمر لإرسال رسالة التكتات الأساسية
@bot.tree.command(name="setup-ticket", description="إرسال رسالة نظام التكتات")
@app_commands.checks.has_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛒 T7 STORE SUPPORT",
        description="مرحباً بك في نظام الدعم الخاص بـ **T7 STORE**.\n\nاضغط على القائمة أدناه واختار سبب فتح التذكرة.",
        color=discord.Color.dark_blue()
    )
    await interaction.channel.send(embed=embed, view=TicketSelectView())
    await interaction.response.send_message("تم إرسال لوحة التكتات بنجاح!", ephemeral=True)

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print(f"تم تسجيل الدخول باسم {bot.user}")
    except Exception as e:
        print(e)

bot.run(TOKEN)
