import random

class RPGMechanics:
    @staticmethod
    def roll_dice(faces: int = 20, modifier: int = 0, tag_bonus: int = 0):
        roll = random.randint(1, faces)
        total = roll + modifier + tag_bonus
        return {
            "roll": roll,
            "modifier": modifier,
            "tag_bonus": tag_bonus,
            "total": total,
            "is_critical": roll == 20,
            "is_fumble": roll == 1
        }

    @staticmethod
    def get_modifier(attribute_value: int):
        return (attribute_value - 10) // 2

    @staticmethod
    def calculate_inventory_slots(inventory: list):
        """Calcula quantos slots estão ocupados"""
        total_slots = 0
        small_items_count = 0
        
        for item in inventory:
            slots = item.get("slots", 1)
            if slots == 0:
                small_items_count += 1
                if small_items_count > 3:
                    total_slots += 1
                    small_items_count = 1
            else:
                total_slots += slots
        return total_slots

    @staticmethod
    def check_success(total: int, dc: int):
        if total >= dc:
            return "Sucesso"
        return "Falha"

    @staticmethod
    def parse_roll_command(command: str):
        """Parse '2d6+5' format"""
        try:
            # Simplificado para 1dX por enquanto
            parts = command.lower().replace(" ", "").split('d')
            num = int(parts[0])
            if '+' in parts[1]:
                faces, mod = map(int, parts[1].split('+'))
            elif '-' in parts[1]:
                faces, mod = map(int, parts[1].split('-'))
                mod = -mod
            else:
                faces = int(parts[1])
                mod = 0
            return num, faces, mod
        except:
            return 1, 20, 0
