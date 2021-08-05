import abc
import dataclasses
import enum

import discord

from .menu import MenuBase


class InlineRollingType(enum.IntEnum):
    DISABLED = 0
    REACTION = 1
    ENABLED = 2


@dataclasses.dataclass
class ServerSettings:
    lookup_dm_role: int = 1234
    lookup_dm_required: bool = True
    lookup_pm_result: bool = False
    inline_enabled: InlineRollingType = InlineRollingType.DISABLED


class ServerSettingsBase(MenuBase, abc.ABC):
    __menu_copy_attrs__ = ('settings', 'guild_name')
    settings: ServerSettings
    guild_name: str


class ServerSettingsUI(ServerSettingsBase):
    @classmethod
    def new(cls, owner: discord.User, settings: ServerSettings, guild_name: str):
        inst = cls(owner=owner)
        inst.settings = settings
        inst.guild_name = guild_name
        return inst

    @discord.ui.button(label='Lookup Settings', style=discord.ButtonStyle.primary)
    async def lookup_settings(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.defer_to(_LookupSettingsUI, interaction)

    @discord.ui.button(label='Inline Rolling Settings', style=discord.ButtonStyle.primary)
    async def inline_rolling_settings(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.defer_to(_InlineRollingSettingsUI, interaction)

    @discord.ui.button(label='Exit', style=discord.ButtonStyle.danger)
    async def exit(self, *_):
        await self.on_timeout()

    def get_content(self):
        embed = discord.Embed(
            title=f"Server Settings for {self.guild_name}",
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name="Lookup Settings",
            value=f"**DM Role**: {self.settings.lookup_dm_role}\n"
                  f"**Monsters Require DM**: {self.settings.lookup_dm_required}\n"
                  f"**Direct Message Results**: {self.settings.lookup_pm_result}",
            inline=False
        )
        embed.add_field(
            name="Inline Rolling Settings",
            value=get_inline_rolling_desc(self.settings.inline_enabled),
            inline=False
        )
        return {"embed": embed}


class _LookupSettingsUI(ServerSettingsBase):
    @discord.ui.button(label='Edit DM Role', style=discord.ButtonStyle.primary)
    async def edit_dm_role(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.settings.lookup_dm_role += 1  # todo follow-up
        await self.refresh_content(interaction)

    @discord.ui.button(label='Toggle DM Requirement', style=discord.ButtonStyle.primary)
    async def toggle_dm_reqired(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.settings.lookup_dm_required = not self.settings.lookup_dm_required
        await self.refresh_content(interaction)

    @discord.ui.button(label='Toggle Result Direct Messaging', style=discord.ButtonStyle.primary)
    async def toggle_pm_result(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.settings.lookup_pm_result = not self.settings.lookup_pm_result
        await self.refresh_content(interaction)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.grey, row=1)
    async def back(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.defer_to(ServerSettingsUI, interaction)

    def get_content(self):
        embed = discord.Embed(
            title=f"Server Settings ({self.guild_name}) / Lookup Settings",
            colour=discord.Colour.blurple(),
            description="These settings affect how lookup results are displayed on this server."
        )
        embed.add_field(
            name="DM Role",
            value=f"**{self.settings.lookup_dm_role}**\n"
                  f"*If `Monsters Require DM` is enabled, any user with this role will be considered a DM.*",
            inline=False
        )
        embed.add_field(
            name="Monsters Require DM",
            value=f"**{self.settings.lookup_dm_required}**\n"
                  f"*If this is enabled, monster lookups will display hidden stats for any user without "
                  f"a role named DM, GM, Dungeon Master, Game Master, or the DM role configured above.*",
            inline=False
        )
        embed.add_field(
            name="Direct Message Results",
            value=f"**{self.settings.lookup_pm_result}**\n"
                  f"*If this is enabled, the result of lookups will be direct messaged to the user who looked "
                  f"it up, rather than being printed to the channel.*",
            inline=False
        )
        return {"embed": embed}


class _InlineRollingSettingsUI(ServerSettingsBase):
    @discord.ui.button(label='Disable', style=discord.ButtonStyle.primary)
    async def disable(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.settings.inline_enabled = InlineRollingType.DISABLED
        await self.refresh_content(interaction)

    @discord.ui.button(label='React', style=discord.ButtonStyle.primary)
    async def react(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.settings.inline_enabled = InlineRollingType.REACTION
        await self.refresh_content(interaction)

    @discord.ui.button(label='Enable', style=discord.ButtonStyle.primary)
    async def enable(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.settings.inline_enabled = InlineRollingType.ENABLED
        await self.refresh_content(interaction)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.grey, row=1)
    async def back(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.defer_to(ServerSettingsUI, interaction)

    def get_content(self):
        embed = discord.Embed(
            title=f"Server Settings ({self.guild_name}) / Inline Rolling Settings",
            colour=discord.Colour.blurple(),
            description=get_inline_rolling_desc(self.settings.inline_enabled)
        )
        return {"embed": embed}


# =================================================================
# Alternate impl - hackier, but shows disabling the selected option
# =================================================================
# class _InlineRollingButton(discord.ui.Button):
#     def __init__(self, setting_value: InlineRollingType, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setting_value = setting_value
#
#     async def callback(self, interaction: discord.Interaction):
#         self.view.settings.inline_enabled = self.setting_value
#         for item in self.view.children:
#             item.disabled = False
#         self.disabled = True
#         await self.view.refresh_content(interaction)
#
#
# class _InlineRollingSettingsUI(ServerSettingsBase):
#     @classmethod
#     def from_menu(cls, other: MenuBase):
#         self = super().from_menu(other)
#         self.add_item(_InlineRollingButton(
#             InlineRollingType.DISABLED, label='Disable', style=discord.ButtonStyle.primary,
#             disabled=self.settings.inline_enabled == InlineRollingType.DISABLED
#         ))
#         self.add_item(_InlineRollingButton(
#             InlineRollingType.REACTION, label='React', style=discord.ButtonStyle.primary,
#             disabled=self.settings.inline_enabled == InlineRollingType.REACTION
#         ))
#         self.add_item(_InlineRollingButton(
#             InlineRollingType.ENABLED, label='Enable', style=discord.ButtonStyle.primary,
#             disabled=self.settings.inline_enabled == InlineRollingType.ENABLED
#         ))
#         return self
#
#     @discord.ui.button(label='Back', style=discord.ButtonStyle.grey, row=1)
#     async def back(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await self.defer_to(ServerSettingsUI, interaction)
#
#     def get_content(self):
#         embed = discord.Embed(
#             title=f"Server Settings ({self.guild_name}) / Inline Rolling Settings",
#             colour=discord.Colour.blurple(),
#             description=get_inline_rolling_desc(self.settings.inline_enabled)
#         )
#         return {"embed": embed}


def get_inline_rolling_desc(inline_enabled: InlineRollingType) -> str:
    if inline_enabled == InlineRollingType.DISABLED:
        return "Inline rolling is currently **disabled**."
    elif inline_enabled == InlineRollingType.REACTION:
        return ("Inline rolling is currently set to **react**. I'll look for messages containing `[[dice]]` "
                "and react with :game_die: - click the reaction to roll!")
    return "Inline rolling is currently **enabled**. I'll roll any `[[dice]]` I find in messages!"
