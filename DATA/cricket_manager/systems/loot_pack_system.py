"""
Loot Pack System - RPG-style progression with credits and random items
"""

import random
from cricket_manager.utils.constants import MAX_SQUAD_SIZE


class LootPackSystem:
    """RPG-style loot pack system for team progression"""
    
    def __init__(self):
        self.pack_cost = 80  # Credits required to open a pack
        
        # Item types and their probabilities
        self.item_types = {
            'youth_player': 0.25,           # 25% chance
            'positive_skill_boost': 0.30,   # 30% chance
            'negative_skill_penalty': 0.10, # 10% chance
            'trait_strength_booster': 0.15, # 15% chance
            'trait_strength_reducer': 0.05, # 5% chance
            'new_trait': 0.15               # 15% chance
        }
        
        # Credit rewards for achievements
        self.credit_rewards = {
            'match_win': 100,
            'match_loss': 25,
            'tournament_win': 500,
            'promotion': 300,
            'century': 50,
            'five_wickets': 50,
            'hat_trick': 100,
            'world_cup_win': 1000,
            'world_cup_runner_up': 500
        }
    
    def earn_credits(self, team, event_type, amount=None):
        """
        Award credits to team for achievements
        
        Args:
            team: Team object
            event_type: Type of achievement
            amount: Optional custom amount (overrides default)
            
        Returns:
            Credits earned
        """
        if amount is None:
            credits = self.credit_rewards.get(event_type, 0)
        else:
            credits = amount
        
        team.credits += credits
        
        print(f"[Credits] {team.name} earned {credits} credits for {event_type}")
        return credits
    
    def can_open_pack(self, team):
        """Check if team has enough credits to open a pack"""
        return team.credits >= self.pack_cost
    
    def open_loot_pack(self, team):
        """
        Open a loot pack and generate random items
        
        Args:
            team: Team object
            
        Returns:
            (items, message) tuple
            items: List of generated items
            message: Success/error message
        """
        # Check credits
        if not self.can_open_pack(team):
            return None, f"Insufficient credits. Need {self.pack_cost}, have {team.credits}"
        
        # Deduct credits
        team.credits -= self.pack_cost
        
        # Generate 3-5 items
        num_items = random.randint(3, 5)
        items = []
        
        for _ in range(num_items):
            item = self.generate_random_item()
            items.append(item)
        
        # Add to team inventory
        team.inventory.extend(items)
        
        print(f"[Loot Pack] {team.name} opened pack and received {num_items} items")
        return items, "Success"
    
    def generate_random_item(self):
        """Generate a random item based on probabilities"""
        # Roll for item type
        roll = random.random()
        cumulative = 0
        selected_type = None
        
        for item_type, probability in self.item_types.items():
            cumulative += probability
            if roll < cumulative:
                selected_type = item_type
                break
        
        # Generate specific item
        if selected_type == 'youth_player':
            return self.generate_youth_player_item()
        elif selected_type == 'positive_skill_boost':
            return self.generate_skill_boost_item(positive=True)
        elif selected_type == 'negative_skill_penalty':
            return self.generate_skill_boost_item(positive=False)
        elif selected_type == 'trait_strength_booster':
            return self.generate_trait_modifier_item(boost=True)
        elif selected_type == 'trait_strength_reducer':
            return self.generate_trait_modifier_item(boost=False)
        elif selected_type == 'new_trait':
            return self.generate_new_trait_item()
        
        # Fallback
        return self.generate_skill_boost_item(positive=True)
    
    def generate_youth_player_item(self):
        """Generate a youth player item"""
        from cricket_manager.core.player import Player
        from cricket_manager.systems.trait_assignment import assign_traits_to_player
        
        # Random role with specific all-rounder types
        roles_with_weights = [
            ('Opening Batter', 15),
            ('Middle Order Batter', 17),
            ('Lower Order Batter', 12),
            ('Wicketkeeper Batter', 10),
            ('Batting Allrounder (Medium Pace)', 2),
            ('Batting Allrounder (Wrist Spin)', 2),
            ('Batting Allrounder (Finger Spin)', 2),
            ('Bowling Allrounder (Medium Pace)', 3),
            ('Bowling Allrounder (Wrist Spin)', 2),
            ('Bowling Allrounder (Finger Spin)', 2),
            ('Bowling Allrounder (Fast Medium)', 2),
            ('Genuine Allrounder (Medium Pace)', 1),
            ('Finger Spinner', 9),
            ('Wrist Spinner', 7),
            ('Medium Pacer', 10),
            ('Fast Medium Pacer', 7),
            ('Fast Bowler', 2),
        ]
        roles = [r[0] for r in roles_with_weights]
        weights = [r[1] for r in roles_with_weights]
        role = random.choices(roles, weights=weights)[0]
        
        age = random.randint(16, 19)
        
        player = Player(f"Youth_{random.randint(1000, 9999)}", age, role, "Generated")
        
        # Youth players have lower current skills but high potential
        player.batting = random.randint(40, 60)
        player.bowling = random.randint(40, 60)
        player.fielding = random.randint(40, 60)
        player.potential = random.randint(70, 95)
        player.is_youth_player = True
        
        # Bonus stats based on role type
        if role in ['Opening Batter', 'Middle Order Batter', 'Lower Order Batter', 'Wicketkeeper Batter']:
            player.batting += random.randint(10, 20)
        elif 'Allrounder' in role:
            # All-rounders get balanced boosts
            player.batting += random.randint(5, 10)
            player.bowling += random.randint(5, 10)
        else:  # Pure bowlers (Spinner, Pacer, Bowler)
            player.bowling += random.randint(10, 20)
        
        # Generate bowling movements for bowlers
        if player.bowling > 40:
            from cricket_manager.systems.bowling_movements import generate_bowling_movements
            player.bowling_movements = generate_bowling_movements(player.bowling, player.role)
        
        # Assign traits (youth players are Tier 5)
        assign_traits_to_player(player, tier=5)
        
        return {
            'type': 'youth_player',
            'player': player,
            'name': f"Youth Player: {player.name}",
            'description': f"{role}, Age {age}, Potential {player.potential}"
        }
    
    def generate_skill_boost_item(self, positive=True):
        """Generate a skill boost/penalty item"""
        skill = random.choice(['batting', 'bowling', 'fielding'])
        
        if positive:
            amount = random.randint(1, 5)
            return {
                'type': 'skill_boost',
                'skill': skill,
                'amount': amount,
                'positive': True,
                'name': f"+{amount} {skill.capitalize()}",
                'description': f"Increases {skill} by {amount} points"
            }
        else:
            amount = -random.randint(1, 3)
            return {
                'type': 'skill_boost',
                'skill': skill,
                'amount': amount,
                'positive': False,
                'name': f"{amount} {skill.capitalize()}",
                'description': f"Decreases {skill} by {abs(amount)} points"
            }
    
    def generate_trait_modifier_item(self, boost=True):
        """Generate a trait strength modifier item"""
        if boost:
            return {
                'type': 'trait_modifier',
                'effect': 'boost',
                'amount': 1,
                'name': "Trait Booster",
                'description': "Increases the strength of a player's trait by 10%"
            }
        else:
            return {
                'type': 'trait_modifier',
                'effect': 'reduce',
                'amount': -1,
                'name': "Trait Reducer",
                'description': "Decreases the strength of a player's trait by 10%"
            }
    
    def generate_new_trait_item(self):
        """Generate a new trait item"""
        from cricket_manager.systems.trait_assignment import ALL_PLAYER_TRAITS, is_positive_trait
        
        # Get all positive traits from player_traits.py
        all_traits = []
        for key, info in ALL_PLAYER_TRAITS.items():
            if is_positive_trait(key):
                all_traits.append(info.get('name', key.replace('_', ' ').title()))
        
        trait = random.choice(all_traits) if all_traits else "Power Opener"
        
        return {
            'type': 'new_trait',
            'trait': trait,
            'name': f"New Trait: {trait}",
            'description': f"Adds the '{trait}' trait to a player"
        }
    
    def apply_item_to_player(self, item, player):
        """
        Apply an item to a player
        
        Args:
            item: Item dictionary
            player: Player object
        
        Returns:
            (success, message) tuple
        """
        item_type = item.get('type')
        
        if item_type == 'skill_boost':
            skill = item['skill']
            amount = item['amount']
            
            # Apply skill change
            if skill == 'batting':
                old_value = player.batting
                player.batting = max(30, min(95, player.batting + amount))
                new_value = player.batting
            elif skill == 'bowling':
                old_value = player.bowling
                player.bowling = max(30, min(95, player.bowling + amount))
                new_value = player.bowling
            elif skill == 'fielding':
                old_value = player.fielding
                player.fielding = max(30, min(95, player.fielding + amount))
                new_value = player.fielding
            else:
                return False, f"Unknown skill: {skill}"
            
            return True, f"{skill.capitalize()} changed from {old_value} to {new_value}"
        
        elif item_type == 'new_trait':
            trait = item['trait']
            
            # Check if player already has this trait
            if trait in player.traits:
                return False, f"Player already has '{trait}' trait"
            
            # Add trait
            player.traits.append(trait)
            return True, f"Added '{trait}' trait to {player.name}"
        
        elif item_type == 'trait_modifier':
            # Trait modifiers are applied to existing traits
            if not player.traits:
                return False, "Player has no traits to modify"
            
            effect = item['effect']
            return True, f"Trait strength {effect}ed"
        
        else:
            return False, "Unknown item type"
    
    def use_item_from_inventory(self, team, item_index, player):
        """
        Use an item from team inventory on a player
        
        Args:
            team: Team object
            item_index: Index of item in team.inventory
            player: Player to apply item to
        
        Returns:
            (success, message) tuple
        """
        # Check if item exists
        if item_index < 0 or item_index >= len(team.inventory):
            return False, "Invalid item index"
        
        item = team.inventory[item_index]
        
        # Special case: youth player items can't be "used" on existing players
        if item['type'] == 'youth_player':
            return False, "Youth players must be added to squad directly"
        
        # Apply item to player
        success, message = self.apply_item_to_player(item, player)
        
        if success:
            # Remove item from inventory
            team.inventory.pop(item_index)
        
        return success, message
    
    def add_youth_player_to_squad(self, team, item_index):
        """
        Add a youth player from inventory to team squad
        
        Args:
            team: Team object
            item_index: Index of youth player item in inventory
        
        Returns:
            (success, message) tuple
        """
        # Check if item exists
        if item_index < 0 or item_index >= len(team.inventory):
            return False, "Invalid item index"
        
        item = team.inventory[item_index]
        
        # Check if it's a youth player
        if item['type'] != 'youth_player':
            return False, "Item is not a youth player"
        
        # Check squad size
        if len(team.players) >= MAX_SQUAD_SIZE:
            return False, f"Squad is full (max {MAX_SQUAD_SIZE} players)"
        
        # Add player to squad
        youth_player = item['player']
        team.players.append(youth_player)
        
        # Remove from inventory
        team.inventory.pop(item_index)
        
        return True, f"Added {youth_player.name} to squad"
