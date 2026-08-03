import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# قاموس لتخزين الشخص الذي استلم التذكرة لكل روم
claimed_tickets = {}

# 1. أزرار التحكم داخل تذكرة الروم (قفل، استلام، إلغاء استلام، استدعاء)
class TicketActionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="قفل التذكرة", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("جاري قفل التذكرة وحذف الروم...", ephemeral=True)
        await interaction.channel.delete()

    @discord.ui.button(label="استلام التذكرة", style=discord.ButtonStyle.success, emoji="🙋‍♂️", custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        claimed_tickets[interaction.channel.id] = interaction.user.id
        await interaction.response.send_message(f"✅ تم استلام التذكرة بواسطة: {interaction.user.mention}")

    @discord.ui.button(label="إلغاء الاستلام", style=discord.ButtonStyle.secondary, emoji="↩️", custom_id="unclaim_ticket")
    async def unclaim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel.id in claimed_tickets:
            del claimed_tickets[interaction.channel.id]
            await interaction.response.send_message(f"🔄 تم إلغاء استلام التذكرة بواسطة: {interaction.user.mention}")
        else:
            await interaction.response.send_message("⚠️ هذه التذكرة لم يتم استلامها أساساً!", ephemeral=True)

    @discord.ui.button(label="استدعاء المسؤول", style=discord.ButtonStyle.primary, emoji="🔔", custom_id="call_staff")
    async def call_staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_id = claimed_tickets.get(interaction.channel.id)
        if staff_id:
            staff_member = interaction.guild.get_member(staff_id)
            if staff_member:
                await interaction.response.send_message(f"🔔 تم استدعاؤك يا {staff_member.mention}! صاحب التذكرة يناديك هنا.")
            else:
                await interaction.response.send_message("⚠️ المسؤول الذي استلم التذكرة غير موجود حالياً في السيرفر.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ لم يتم استلام هذه التذكرة من قبل أي مسؤول حتى يتم استدعاؤه!", ephemeral=True)


# 2. القائمة المنسدلة مطابقة لصورتك تماماً
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="الدعم الفني", 
                description="فتح تذكره لطلب الدعم الفني و الاستفسار", 
                emoji="🛠️", 
                value="الدعم الفني"
            ),
            discord.SelectOption(
                label="طلب وسيط", 
                description="طلب وسيط لضمان حقك", 
                emoji="🤝", 
                value="طلب وسيط"
            ),
            discord.SelectOption(
                label="شراء", 
                description="هذا الخيار مخصص لشراء منتج او شي ثاني", 
                emoji="🛒", 
                value="شراء"
            ),
            discord.SelectOption(
                label="قسم إضافي", 
                description="خيار مخصص حسب طلبك", 
                emoji="📌", 
                value="قسم إضافي"
            ),
            discord.SelectOption(
                label="مشكله في الحساب", 
                description="مثال لهذه الخيار مثال اذا الحساب مبند او كلمه السر غير صحيحه", 
                emoji="⚠️", 
                value="مشكله في الحساب"
            )
        ]
        super().__init__(placeholder="اختر خيار التذكرة", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu_v3")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = interaction.channel.category

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        ticket_name = f"ticket-{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(ticket_name, overwrites=overwrites, category=category)

        embed = discord.Embed(
            title=f"🎫 تذكرة جديدة: {self.values[0]}",
            description=f"مرحباً بك {interaction.user.mention}\nتم فتح التذكرة بنجاح، يرجى الانتظار لحين رد الإدارة.",
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=embed, view=TicketActionView())
        await interaction.response.send_message(f"✅ تم فتح تذكرتك بنجاح: {ticket_channel.mention}", ephemeral=True)


class TicketSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    embed = discord.Embed(
        title="🎫 نظام تذاكر متجر T7",
        description="اختر خيار التذكرة المناسب لك من القائمة أدناه:",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketSelectView())


TOKEN = os.getenv("TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: TOKEN environment variable not found!")
    
