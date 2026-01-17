import cv2
import mediapipe as mp
import numpy as np
import time
import os
import random
import math
from datetime import datetime

class ChemicalReaction:
    def __init__(self, reactants, products, animation_type, color_change=None, text="", duration=3.0):
        self.reactants = set(reactants)
        self.products = products
        self.animation_type = animation_type  # 'fire', 'fizz', 'color_change', 'smoke', 'foam'
        self.color_change = color_change
        self.text = text
        self.duration = duration

class ChemistryEngine:
    def __init__(self):
        self.reactions = {
            frozenset(['Sodium', 'Water']): ChemicalReaction(
                ['Sodium', 'Water'], 'Hydrogen Gas + Heat',
                'fire', None,
                "Sodium reacts vigorously with water to produce hydrogen gas, which catches fire!", 4.0
            ),
            frozenset(['Acid', 'Base']): ChemicalReaction(
                ['Acid', 'Base'], 'Water + Salt',
                'color_change', (128, 255, 128),
                "Acid neutralizes base producing water and salt. Heat is released!", 3.5
            ),
            frozenset(['Ethanol', 'Heat']): ChemicalReaction(
                ['Ethanol', 'Heat'], 'Blue Flame',
                'blue_fire', (255, 128, 0),
                "Ethanol burns with a clean blue flame, producing CO2 and water!", 3.0
            ),
            frozenset(['Sugar', 'Acid']): ChemicalReaction(
                ['Sugar', 'Acid'], 'Carbon Column',
                'foam', (20, 20, 20),
                "Sulfuric acid dehydrates sugar, creating a growing carbon column!", 5.0
            ),
            frozenset(['Copper_Sulfate', 'Ammonia']): ChemicalReaction(
                ['Copper_Sulfate', 'Ammonia'], 'Deep Blue Complex',
                'color_change', (200, 100, 0),
                "Copper sulfate forms a beautiful deep blue complex with ammonia!", 3.0
            ),
            frozenset(['Magnesium', 'Heat']): ChemicalReaction(
                ['Magnesium', 'Heat'], 'Bright White Light',
                'bright_flash', (255, 255, 255),
                "Magnesium burns with an intense white light - don't look directly!", 2.5
            ),
        }
        
        self.active_reactions = []
        self.particles = []

    def check_reaction(self, chemicals_in_beaker):
        chemical_set = frozenset(chemicals_in_beaker)
        for reaction_key, reaction in self.reactions.items():
            if reaction_key.issubset(chemical_set):
                return reaction
        return None

    def start_reaction(self, reaction, position):
        self.active_reactions.append({
            'reaction': reaction,
            'position': position,
            'start_time': time.time(),
            'particles': []
        })

    def update_reactions(self, canvas):
        current_time = time.time()
        active_reactions_copy = self.active_reactions.copy()
        
        for reaction_data in active_reactions_copy:
            elapsed = current_time - reaction_data['start_time']
            if elapsed > reaction_data['reaction'].duration:
                self.active_reactions.remove(reaction_data)
                continue
                
            self.render_reaction(canvas, reaction_data, elapsed)

    def render_reaction(self, canvas, reaction_data, elapsed):
        reaction = reaction_data['reaction']
        pos = reaction_data['position']
        progress = elapsed / reaction.duration
        
        if reaction.animation_type == 'fire':
            self.render_fire_animation(canvas, pos, progress)
        elif reaction.animation_type == 'blue_fire':
            self.render_blue_fire_animation(canvas, pos, progress)
        elif reaction.animation_type == 'fizz':
            self.render_fizz_animation(canvas, pos, progress)
        elif reaction.animation_type == 'color_change':
            self.render_color_change(canvas, pos, reaction.color_change, progress)
        elif reaction.animation_type == 'foam':
            self.render_foam_animation(canvas, pos, progress)
        elif reaction.animation_type == 'bright_flash':
            self.render_bright_flash(canvas, pos, progress)
        elif reaction.animation_type == 'smoke':
            self.render_smoke_animation(canvas, pos, progress)

    def render_fire_animation(self, canvas, pos, progress):
        x, y = pos
        intensity = max(0, 1 - progress)
        
        # Multiple flame particles
        for i in range(8):
            flame_x = x + random.randint(-30, 30)
            flame_y = y - random.randint(10, 60) - int(progress * 40)
            size = random.randint(8, 20) * intensity
            
            if size > 2:
                # Red-orange-yellow gradient
                color = (random.randint(0, 100), random.randint(100, 200), random.randint(200, 255))
                cv2.circle(canvas, (int(flame_x), int(flame_y)), int(size), color, -1)

    def render_blue_fire_animation(self, canvas, pos, progress):
        x, y = pos
        intensity = max(0, 1 - progress)
        
        for i in range(6):
            flame_x = x + random.randint(-20, 20)
            flame_y = y - random.randint(5, 40) - int(progress * 30)
            size = random.randint(6, 15) * intensity
            
            if size > 2:
                # Blue flame colors
                color = (random.randint(200, 255), random.randint(50, 150), random.randint(0, 100))
                cv2.circle(canvas, (int(flame_x), int(flame_y)), int(size), color, -1)

    def render_fizz_animation(self, canvas, pos, progress):
        x, y = pos
        
        for i in range(15):
            bubble_x = x + random.randint(-40, 40)
            bubble_y = y - random.randint(0, 80) - int(progress * 50)
            size = random.randint(2, 8)
            
            color = (random.randint(200, 255), random.randint(200, 255), random.randint(150, 255))
            cv2.circle(canvas, (int(bubble_x), int(bubble_y)), size, color, 2)

    def render_color_change(self, canvas, pos, color, progress):
        x, y = pos
        radius = int(30 + progress * 50)
        alpha = max(0.3, 1 - progress * 0.5)
        
        overlay = canvas.copy()
        cv2.circle(overlay, (x, y), radius, color, -1)
        cv2.addWeighted(canvas, 1 - alpha, overlay, alpha, 0, canvas)

    def render_foam_animation(self, canvas, pos, progress):
        x, y = pos
        
        # Growing foam column
        foam_height = int(progress * 100)
        for i in range(0, foam_height, 5):
            foam_y = y - i
            width = max(5, 40 - i // 3)
            color = (random.randint(10, 50), random.randint(10, 50), random.randint(10, 50))
            cv2.circle(canvas, (x + random.randint(-width//2, width//2), foam_y), 
                      random.randint(3, 10), color, -1)

    def render_bright_flash(self, canvas, pos, progress):
        x, y = pos
        if progress < 0.3:  # Flash only in first 30% of animation
            intensity = (0.3 - progress) / 0.3
            radius = int(60 * intensity)
            overlay = canvas.copy()
            cv2.circle(overlay, (x, y), radius, (255, 255, 255), -1)
            cv2.addWeighted(canvas, 1 - intensity * 0.8, overlay, intensity * 0.8, 0, canvas)

    def render_smoke_animation(self, canvas, pos, progress):
        x, y = pos
        
        for i in range(10):
            smoke_x = x + random.randint(-50, 50) + int(progress * random.randint(-30, 30))
            smoke_y = y - random.randint(20, 100) - int(progress * 60)
            size = random.randint(5, 20)
            
            color = (random.randint(100, 150), random.randint(100, 150), random.randint(100, 150))
            cv2.circle(canvas, (int(smoke_x), int(smoke_y)), size, color, -1)

class RamperVirtualPainter:
    def __init__(self, cam_index=None, width=1280, height=720, command_queue=None):
        # Video capture is handled externally in web mode, or via run() in local mode
        self.cam_index = cam_index
        self.command_queue = command_queue
        self.width = width
        self.height = height

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.canvas = None
        self.prev_x, self.prev_y = None, None
        self.smoothed_x, self.smoothed_y = 0, 0
        self.smoothing_factor = 0.25
        self.last_draw_time = 0.0
        self.draw_timeout = 0.25

        self.brush_thickness = 8
        self.eraser_thickness = 40
        self.is_eraser = False

        # Adaptive toolbar dimensions for better screen utilization
        self.toolbar_height = int(max(60, height * 0.14))
        self.instruction_height = int(max(40, height * 0.11))
        
        # Adaptive status panel
        self.status_panel_width = int(max(200, width * 0.27))
        
        # Application modes
        self.app_mode = "PAINTER"  # PAINTER or CHEMISTRY
        
        # Painter mode colors
        self.color_list = [
            (255, 0, 255),   # Purple
            (255, 0, 0),     # Blue
            (0, 255, 0),     # Green
            (0, 0, 255),     # Red
            (0, 165, 255),   # Orange
            (0, 255, 255),   # Yellow
            (255, 255, 255), # White
            (0, 0, 0)        # Black [Eraser]
        ]
        self.color_names = [
            "PUR", "BLU", "GRN", "RED", "ORG", "YEL", "WHT", "BLK"
        ]
        
        # Chemistry mode chemicals
        self.chemicals = [
            "Sodium", "Water", "Acid", "Base", "Ethanol", "Sugar", "Copper_Sulfate", 
            "Ammonia", "Heat", "Magnesium"
        ]
        self.chemical_colors = [
            (192, 192, 192),  # Sodium - Silver
            (255, 255, 200),  # Water - Light Blue
            (0, 100, 255),    # Acid - Red
            (255, 100, 0),    # Base - Blue  
            (200, 255, 200),  # Ethanol - Light Green
            (255, 255, 255),  # Sugar - White
            (200, 100, 0),    # Copper Sulfate - Blue
            (100, 200, 100),  # Ammonia - Light Green
            (0, 140, 255),    # Heat - Orange
            (220, 220, 220),  # Magnesium - Light Gray
        ]
        
        self.selected_color_idx = 0
        self.selected_color = self.color_list[self.selected_color_idx]
        self.selected_chemical = self.chemicals[0]

        # Chemistry lab components
        self.chemistry_engine = ChemistryEngine()
        self.beakers = [
            {"pos": (300, 350), "radius": 60, "chemicals": [], "color": (100, 100, 100)},
            {"pos": (600, 350), "radius": 60, "chemicals": [], "color": (100, 100, 100)},
            {"pos": (900, 350), "radius": 60, "chemicals": [], "color": (100, 100, 100)},
        ]
        self.dragging_chemical = None
        self.educational_text = ""
        self.educational_text_time = 0

        # Mode states
        self.mode = "IDLE"  # IDLE / DRAW / SELECT
        self.last_mode_change = time.time()
        self.mode_debounce = 0.12

        self.save_dir = "saved_paintings"
        os.makedirs(self.save_dir, exist_ok=True)

    def fingers_up(self, landmarks, w, h):
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        tip_ids = [4, 8, 12, 16, 20]
        pip_ids = [3, 6, 10, 14, 18]
        fingers = []

        try:
            if pts[tip_ids[0]][0] < pts[pip_ids[0]][0]:
                fingers.append(1)
            else:
                fingers.append(0)
        except:
            fingers.append(0)

        for i in range(1, 5):
            try:
                if pts[tip_ids[i]][1] < pts[pip_ids[i]][1] - 12:
                    fingers.append(1)
                else:
                    fingers.append(0)
            except:
                fingers.append(0)

        return fingers, pts

    def draw_rounded_rect(self, img, pt1, pt2, color, thickness=1, radius=10, filled=False):
        x1, y1 = pt1
        x2, y2 = pt2
        
        # Clamp radius
        w = x2 - x1
        h = y2 - y1
        radius = min(radius, w//2, h//2)
        
        # Corners
        corners = [
            ((x1 + radius, y1 + radius), 180, 270), # Top-left
            ((x2 - radius, y1 + radius), 270, 360), # Top-right
            ((x2 - radius, y2 - radius), 0, 90),    # Bottom-right
            ((x1 + radius, y2 - radius), 90, 180)   # Bottom-left
        ]
        
        if filled:
            # Draw filled rectangle with rounded corners hack
            # Center rect
            cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1)
            # Side rects
            cv2.rectangle(img, (x1, y1 + radius), (x1 + radius, y2 - radius), color, -1)
            cv2.rectangle(img, (x2 - radius, y1 + radius), (x2, y2 - radius), color, -1)
            # Corner circles
            cv2.circle(img, (x1 + radius, y1 + radius), radius, color, -1)
            cv2.circle(img, (x2 - radius, y1 + radius), radius, color, -1)
            cv2.circle(img, (x2 - radius, y2 - radius), radius, color, -1)
            cv2.circle(img, (x1 + radius, y2 - radius), radius, color, -1)
        else:
            # Draw outline
            # Lines
            cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
            cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
            cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
            cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness)
            # Arcs
            for center, start_angle, end_angle in corners:
                cv2.ellipse(img, center, (radius, radius), 0, start_angle, end_angle, color, thickness)

    def draw_painter_toolbar(self, frame):
        h, w, _ = frame.shape
        
        # Modern Dark Glassmorphism Header
        header_height = self.toolbar_height + 25
        header_bg = frame[0:header_height, 0:w].copy()
        rect = np.full(header_bg.shape, (20, 20, 20), dtype=np.uint8)
        frame[0:header_height, 0:w] = cv2.addWeighted(header_bg, 0.3, rect, 0.7, 0)
        
        # Bottom border for header
        cv2.line(frame, (0, header_height), (w, header_height), (100, 100, 100), 1)

        # Mode Selection Pill (Top Right)
        mode_btn_w = 160
        mode_btn_h = 40
        mode_btn_x = w - mode_btn_w - 20
        mode_btn_y = 20
        
        # Draw Mode Button (Outline style)
        self.draw_rounded_rect(frame, (mode_btn_x, mode_btn_y), 
                             (mode_btn_x + mode_btn_w, mode_btn_y + mode_btn_h),
                             (0, 200, 255), thickness=1, radius=20, filled=False)
        
        cv2.putText(frame, "SWITCH MODE", (mode_btn_x + 25, mode_btn_y + 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1, cv2.LINE_AA)

        # Color/Tool Cards
        available_width = w - mode_btn_w - 60
        slots = len(self.color_list)
        
        # Calculate optimal card size based on available width
        card_spacing = 15
        card_width = int((available_width - (slots + 1) * card_spacing) / slots)
        card_width = min(card_width, 100) # Max width constraint
        card_height = 80
        
        start_x = 20
        start_y = 15
        
        for i, col in enumerate(self.color_list):
            x1 = start_x + i * (card_width + card_spacing)
            y1 = start_y
            x2 = x1 + card_width
            y2 = y1 + card_height
            
            # Is selected?
            is_selected = (i == self.selected_color_idx)
            is_eraser_tool = (i == len(self.color_list) - 1)
            
            # Card Background
            bg_color = (40, 40, 40)
            if is_selected:
                bg_color = (70, 70, 70)
            
            self.draw_rounded_rect(frame, (x1, y1), (x2, y2), bg_color, radius=12, filled=True)
            
            # Color Preview Circle
            center_x = (x1 + x2) // 2
            circle_y = y1 + 35
            radius = 20
            
            if is_eraser_tool:
                # Eraser Icon (Hollow Circle)
                cv2.circle(frame, (center_x, circle_y), radius, (200, 200, 200), 2)
                cv2.line(frame, (center_x-10, circle_y-10), (center_x+10, circle_y+10), (200, 200, 200), 2)
            else:
                # Color Circle
                cv2.circle(frame, (center_x, circle_y), radius, col, -1)
                # Border for dark colors
                if sum(col) < 100:
                    cv2.circle(frame, (center_x, circle_y), radius, (100, 100, 100), 1)

            # Label
            label = "Eraser" if is_eraser_tool else self.color_names[i]
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            text_x = center_x - text_size[0] // 2
            
            text_col = (200, 200, 200)
            if is_selected:
                text_col = (255, 255, 255)
                # Selection Indicator (Active Border)
                self.draw_rounded_rect(frame, (x1, y1), (x2, y2), (255, 255, 255), thickness=2, radius=12)
                
            cv2.putText(frame, label, (text_x, y2 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_col, 1, cv2.LINE_AA)

        # Instructions Pill at the bottom center of video (Floating)
        instr_text = "👆 Point to Draw  |  ✌️ Select Color  |  ✋ Clear (C)"
        self.draw_floating_pill(frame, instr_text, w, h - 50)

    def draw_chemistry_toolbar(self, frame):
        h, w, _ = frame.shape
        
        # Modern Dark Glassmorphism Header
        header_height = self.toolbar_height + 25
        header_bg = frame[0:header_height, 0:w].copy()
        rect = np.full(header_bg.shape, (20, 30, 25), dtype=np.uint8) # Slightly greenish tint for chemistry
        frame[0:header_height, 0:w] = cv2.addWeighted(header_bg, 0.3, rect, 0.7, 0)
        cv2.line(frame, (0, header_height), (w, header_height), (100, 150, 100), 1)

        # Mode Selection Pill (Top Right)
        mode_btn_w = 160
        mode_btn_h = 40
        mode_btn_x = w - mode_btn_w - 20
        mode_btn_y = 20
        
        self.draw_rounded_rect(frame, (mode_btn_x, mode_btn_y), 
                             (mode_btn_x + mode_btn_w, mode_btn_y + mode_btn_h),
                             (0, 255, 100), thickness=1, radius=20, filled=False)
        
        cv2.putText(frame, "SWITCH MODE", (mode_btn_x + 25, mode_btn_y + 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 100), 1, cv2.LINE_AA)

        # Chemical Cards
        available_width = w - mode_btn_w - 60
        slots = len(self.chemicals)
        
        card_spacing = 10
        card_width = int((available_width - (slots + 1) * card_spacing) / slots)
        card_width = min(card_width, 110)
        card_height = 80
        
        start_x = 20
        start_y = 15
        
        for i, chem in enumerate(self.chemicals):
            x1 = start_x + i * (card_width + card_spacing)
            y1 = start_y
            x2 = x1 + card_width
            y2 = y1 + card_height
            
            is_selected = (chem == self.selected_chemical)
            
            # Card Background
            bg_color = (35, 45, 35)
            if is_selected:
                bg_color = (50, 80, 50)
                
            self.draw_rounded_rect(frame, (x1, y1), (x2, y2), bg_color, radius=10, filled=True)
            
            # Chemical Element Style Preview
            chem_color = self.chemical_colors[i]
            
            # Colored bar at top of card
            self.draw_rounded_rect(frame, (x1, y1), (x2, y1 + 6), chem_color, radius=10, filled=True)
            # Fix bottom corners of the bar being rounded by overdrawing with rect
            cv2.rectangle(frame, (x1, y1+3), (x2, y1+6), chem_color, -1)
            
            
            # Chemical Name
            # Split if too long
            font_scale = 0.35
            text_col = (220, 220, 220)
            if is_selected:
                text_col = (255, 255, 255)
                self.draw_rounded_rect(frame, (x1, y1), (x2, y2), (0, 255, 100), thickness=2, radius=10)

            if len(chem) > 9:
                line1 = chem[:9]
                line2 = chem[9:]
                cv2.putText(frame, line1, (x1 + 8, y1 + 35), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_col, 1, cv2.LINE_AA)
                cv2.putText(frame, line2, (x1 + 8, y1 + 55), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_col, 1, cv2.LINE_AA)
            else:
                cv2.putText(frame, chem, (x1 + 8, y1 + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_col, 1, cv2.LINE_AA)

        # Instructions Pill
        instr_text = "✌️ Select Chemical  |  🤏 Drag to Beaker  |  🧪 Mix"
        self.draw_floating_pill(frame, instr_text, w, h - 50)

    def draw_floating_pill(self, frame, text, w, y_pos):
        # Draw a floating pill with instructions
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        pill_w = text_size[0] + 40
        pill_h = 40
        pill_x = (w - pill_w) // 2
        
        # Transparent background
        overlay = frame.copy()
        self.draw_rounded_rect(overlay, (pill_x, y_pos), (pill_x + pill_w, y_pos + pill_h), (0, 0, 0), radius=20, filled=True)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        cv2.putText(frame, text, (pill_x + 20, y_pos + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    def draw_chemistry_lab(self, frame):
        h, w, _ = frame.shape
        
        # Position beakers better for full screen utilization
        lab_start_y = self.toolbar_height + self.instruction_height
        lab_height = h - lab_start_y - 150  # Reserve space for educational text
        
        # Update beaker positions for better spacing
        beaker_y = lab_start_y + lab_height // 2
        spacing = (w - 200) // (len(self.beakers) + 1)
        
        for i, beaker in enumerate(self.beakers):
            beaker["pos"] = (100 + spacing * (i + 1), beaker_y)
        
        # Draw beakers
        for i, beaker in enumerate(self.beakers):
            pos = beaker["pos"]
            radius = beaker["radius"]
            
            # Beaker outline with better styling
            cv2.circle(frame, pos, radius, (180, 180, 180), 3)
            cv2.circle(frame, pos, radius - 5, (120, 120, 120), 2)
            
            # Beaker base
            base_rect = (pos[0] - radius + 10, pos[1] + radius - 15, 
                        pos[0] + radius - 10, pos[1] + radius + 5)
            cv2.rectangle(frame, (base_rect[0], base_rect[1]), (base_rect[2], base_rect[3]), 
                         (150, 150, 150), 2)
            
            # Beaker contents (mixed chemical colors)
            if beaker["chemicals"]:
                mixed_color = self.mix_chemical_colors(beaker["chemicals"])
                cv2.circle(frame, (pos[0], pos[1] + 12), radius - 12, mixed_color, -1)
                
                # Chemical names in beaker - better formatting
                y_offset = pos[1] - radius - 15
                for j, chem in enumerate(beaker["chemicals"]):
                    cv2.putText(frame, chem[:10], (pos[0] - 40, y_offset - j * 18),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
            
            # Beaker label with better styling
            cv2.putText(frame, f"Beaker {i+1}", (pos[0] - 40, pos[1] + radius + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 2, cv2.LINE_AA)

        # Draw educational text with improved layout
        if self.educational_text and time.time() - self.educational_text_time < 6:
            text_y = h - 140
            
            # Background for text with better opacity
            cv2.rectangle(frame, (15, text_y - 45), (w - 15, h - 15), (30, 30, 30), -1)
            cv2.rectangle(frame, (15, text_y - 45), (w - 15, h - 15), (100, 255, 100), 2)
            
            # Wrap long text more efficiently
            max_chars_per_line = min(90, w // 10)  # Adaptive line length based on screen width
            words = self.educational_text.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + word) < max_chars_per_line:
                    current_line += word + " "
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            
            # Draw educational text lines
            for i, line in enumerate(lines[:3]):  # Max 3 lines
                cv2.putText(frame, line, (25, text_y - 25 + i * 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 255, 120), 1, cv2.LINE_AA)

    def mix_chemical_colors(self, chemicals):
        if not chemicals:
            return (100, 100, 100)
        
        total_r, total_g, total_b = 0, 0, 0
        for chemical in chemicals:
            if chemical in self.chemicals:
                idx = self.chemicals.index(chemical)
                color = self.chemical_colors[idx]
                total_r += color[0]
                total_g += color[1] 
                total_b += color[2]
        
        count = len(chemicals)
        return (total_r // count, total_g // count, total_b // count)

    def select_from_painter_toolbar(self, x, y, frame_w):
        if y > self.toolbar_height:
            return False
            
        # Check mode switch button - updated coordinates
        mode_button_width = 140
        mode_btn_x = frame_w - mode_button_width - 10
        if x >= mode_btn_x and x <= frame_w - 10:
            self.app_mode = "CHEMISTRY"
            self.canvas = np.zeros_like(self.canvas) if self.canvas is not None else None
            return True
            
        # Check color slots
        available_width = frame_w - mode_button_width - 30
        slots = len(self.color_list)
        padding = 12
        total_padding = padding * (slots + 1)
        slot_width = max(65, (available_width - total_padding) // slots)

        for i in range(slots):
            x1 = padding + i * (slot_width + padding)
            x2 = x1 + slot_width
            if x1 <= x <= x2:
                self.selected_color_idx = i
                self.selected_color = self.color_list[i]
                self.is_eraser = (i == slots - 1)
                return True
        return False

    def select_from_chemistry_toolbar(self, x, y, frame_w):
        if y > self.toolbar_height:
            return False
            
        # Check mode switch button - updated coordinates
        mode_button_width = 120
        mode_btn_x = frame_w - mode_button_width - 10
        if x >= mode_btn_x and x <= frame_w - 10:
            self.app_mode = "PAINTER"
            self.canvas = np.zeros_like(self.canvas) if self.canvas is not None else None
            return True
            
        # Check chemical slots
        available_width = frame_w - mode_button_width - 30
        slots = len(self.chemicals)
        padding = 8
        total_padding = padding * (slots + 1)
        slot_width = max(60, (available_width - total_padding) // slots)

        for i in range(slots):
            x1 = padding + i * (slot_width + padding)
            x2 = x1 + slot_width
            if x1 <= x <= x2:
                self.selected_chemical = self.chemicals[i]
                return True
        return False

    def find_beaker_at_position(self, x, y):
        for i, beaker in enumerate(self.beakers):
            pos = beaker["pos"]
            radius = beaker["radius"]
            distance = math.sqrt((x - pos[0])**2 + (y - pos[1])**2)
            if distance <= radius:
                return i
        return None

    def check_chemical_reactions(self, beaker_idx):
        beaker = self.beakers[beaker_idx]
        if len(beaker["chemicals"]) >= 2:
            reaction = self.chemistry_engine.check_reaction(beaker["chemicals"])
            if reaction:
                self.chemistry_engine.start_reaction(reaction, beaker["pos"])
                self.educational_text = reaction.text
                self.educational_text_time = time.time()
                
                # Clear beaker after reaction
                beaker["chemicals"] = []

    def save_canvas(self):
        if self.app_mode == "PAINTER":
            fname = datetime.now().strftime("FunDraw_painting_%Y%m%d_%H%M%S.png")
        else:
            fname = datetime.now().strftime("FunDraw_chemistry_%Y%m%d_%H%M%S.png")
        save_path = os.path.join(self.save_dir, fname)
        cv2.imwrite(save_path, self.canvas)
        print(f"[FunDraw_ChemLab] Saved {self.app_mode.lower()} to {save_path}")

    def process_frame(self, frame):
        # Process external commands
        if self.command_queue:
            while not self.command_queue.empty():
                try:
                    cmd = self.command_queue.get_nowait()
                    if cmd["type"] == "clear":
                        self.canvas = np.zeros_like(self.canvas)
                    elif cmd["type"] == "save":
                        self.save_canvas()
                    elif cmd["type"] == "mode":
                        self.app_mode = cmd["value"]
                        self.canvas = np.zeros_like(self.canvas)
                    elif cmd["type"] == "brush_size":
                         if cmd["action"] == "increase":
                             self.brush_thickness = min(self.brush_thickness + 2, 60)
                         else:
                             self.brush_thickness = max(self.brush_thickness - 2, 2)
                except:
                    pass

        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Ensure canvas matches frame size
        if self.canvas is None or self.canvas.shape != frame.shape:
             self.canvas = np.zeros_like(frame)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        # Draw appropriate toolbar
        if self.app_mode == "PAINTER":
            self.draw_painter_toolbar(frame)
        else:
            self.draw_chemistry_toolbar(frame)
            self.draw_chemistry_lab(frame)

        current_time = time.time()
        detected_fingers = None

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            fingers, pts = self.fingers_up(hand_landmarks.landmark, w, h)
            detected_fingers = fingers

            try:
                index_tip = pts[8]
                thumb_tip = pts[4]
            except:
                index_tip = (0, 0)
                thumb_tip = (0, 0)

            x1, y1 = index_tip

            if self.smoothed_x == 0 and self.smoothed_y == 0:
                self.smoothed_x, self.smoothed_y = x1, y1
            else:
                self.smoothed_x = int(self.smoothed_x + (x1 - self.smoothed_x) * (1 - self.smoothing_factor))
                self.smoothed_y = int(self.smoothed_y + (y1 - self.smoothed_y) * (1 - self.smoothing_factor))

            if self.app_mode == "PAINTER":
                self.handle_painter_gestures(fingers, current_time, frame, w)
            else:
                self.handle_chemistry_gestures(fingers, current_time, frame, w, thumb_tip)

            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        else:
            if time.time() - self.last_draw_time > self.draw_timeout:
                self.prev_x, self.prev_y = None, None
            detected_fingers = None
            self.dragging_chemical = None

        # Update chemistry reactions
        if self.app_mode == "CHEMISTRY":
            self.chemistry_engine.update_reactions(self.canvas)

        # Merge canvas with better blending
        if self.app_mode == "PAINTER" or (self.chemistry_engine and self.chemistry_engine.active_reactions) or np.any(self.canvas > 0):
             img_gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
             _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
             img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
             frame = cv2.bitwise_and(frame, img_inv)
             frame = cv2.bitwise_or(frame, self.canvas)

        # Draw status panel
        self.draw_status_panel(frame, w, h, detected_fingers)

        return frame

    def handle_painter_gestures(self, fingers, current_time, frame, w):
        # Selection mode: index and middle up
        if fingers[1] == 1 and fingers[2] == 1:
            if current_time - self.last_mode_change > self.mode_debounce:
                self.mode = "SELECT"
                self.last_mode_change = current_time
        # Drawing mode: index up
        elif fingers[1] == 1:
            if current_time - self.last_mode_change > self.mode_debounce:
                self.mode = "DRAW"
                self.last_mode_change = current_time
        else:
            if current_time - self.last_mode_change > self.mode_debounce:
                self.mode = "IDLE"
                self.last_mode_change = current_time

        # Act on mode
        if self.mode == "SELECT":
            cv2.circle(frame, (self.smoothed_x, self.smoothed_y), 16, (0, 255, 0), 3)
            if self.smoothed_y <= self.toolbar_height:
                self.select_from_painter_toolbar(self.smoothed_x, self.smoothed_y, w)
                cv2.putText(frame, f"Selected: {self.color_names[self.selected_color_idx]}",
                            (15, self.toolbar_height + self.instruction_height + 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 2, cv2.LINE_AA)
                time.sleep(0.09)
            self.prev_x, self.prev_y = None, None

        elif self.mode == "DRAW":
            draw_color = (0, 0, 0) if self.is_eraser else self.selected_color
            thickness = self.eraser_thickness if self.is_eraser else self.brush_thickness
            cv2.circle(frame, (self.smoothed_x, self.smoothed_y), max(8, thickness // 2), draw_color, 2)

            # Only draw below the instruction area
            draw_zone_start = self.toolbar_height + self.instruction_height
            if self.smoothed_y > draw_zone_start:
                if self.prev_x is None or self.prev_y is None:
                    self.prev_x, self.prev_y = self.smoothed_x, self.smoothed_y
                self.draw_smooth_line(self.canvas, (self.prev_x, self.prev_y),
                                      (self.smoothed_x, self.smoothed_y),
                                      draw_color, thickness)
                self.prev_x, self.prev_y = self.smoothed_x, self.smoothed_y
                self.last_draw_time = current_time
            else:
                if current_time - self.last_draw_time > self.draw_timeout:
                    self.prev_x, self.prev_y = None, None
        else:  # IDLE
            if current_time - self.last_draw_time > self.draw_timeout:
                self.prev_x, self.prev_y = None, None

    def handle_chemistry_gestures(self, current_time, frame, w, thumb_tip):
        # Chemical selection: two fingers up (index + middle)
        if fingers[1] == 1 and fingers[2] == 1 and not self.dragging_chemical:
            if current_time - self.last_mode_change > self.mode_debounce:
                self.mode = "SELECT"
                self.last_mode_change = current_time
        # Chemical dragging: pinch gesture (thumb + index close together)
        elif fingers[0] == 1 and fingers[1] == 1 and not self.dragging_chemical:
            thumb_x, thumb_y = thumb_tip
            distance = math.sqrt((self.smoothed_x - thumb_x)**2 + (self.smoothed_y - thumb_y)**2)
            if distance < 50:  # Pinch detected
                if current_time - self.last_mode_change > self.mode_debounce:
                    self.mode = "DRAG"
                    self.dragging_chemical = self.selected_chemical
                    self.last_mode_change = current_time
        # Continue dragging if already dragging
        elif self.dragging_chemical:
            self.mode = "DRAG"
        else:
            if current_time - self.last_mode_change > self.mode_debounce:
                self.mode = "IDLE"
                self.last_mode_change = current_time

        # Act on mode
        if self.mode == "SELECT":
            cv2.circle(frame, (self.smoothed_x, self.smoothed_y), 16, (0, 255, 0), 3)
            if self.smoothed_y <= self.toolbar_height:
                self.select_from_chemistry_toolbar(self.smoothed_x, self.smoothed_y, w)
                cv2.putText(frame, f"Selected: {self.selected_chemical}",
                            (15, self.toolbar_height + self.instruction_height + 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 200), 2, cv2.LINE_AA)
                time.sleep(0.09)

        elif self.mode == "DRAG" and self.dragging_chemical:
            # Show dragging cursor with chemical name
            cv2.circle(frame, (self.smoothed_x, self.smoothed_y), 22, (255, 255, 0), 3)
            cv2.putText(frame, self.dragging_chemical[:10], 
                        (self.smoothed_x - 40, self.smoothed_y - 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2, cv2.LINE_AA)
            
            # Check if over a beaker
            beaker_idx = self.find_beaker_at_position(self.smoothed_x, self.smoothed_y)
            if beaker_idx is not None:
                # Highlight beaker
                pos = self.beakers[beaker_idx]["pos"]
                radius = self.beakers[beaker_idx]["radius"]
                cv2.circle(frame, pos, radius + 8, (255, 255, 0), 4)
                
                # Drop chemical into beaker
                if fingers[0] == 0 or fingers[1] == 0:  # Release pinch
                    if self.dragging_chemical not in self.beakers[beaker_idx]["chemicals"]:
                        self.beakers[beaker_idx]["chemicals"].append(self.dragging_chemical)
                        print(f"[FunDraw_ChemLab] Added {self.dragging_chemical} to Beaker {beaker_idx + 1}")
                    self.dragging_chemical = None

            # Stop dragging if pinch released
            if fingers[0] == 0 or fingers[1] == 0:
                self.dragging_chemical = None

    def draw_status_panel(self, frame, w, h, detected_fingers):
        # Better positioning for status panel to utilize full screen
        status_width = self.status_panel_width
        status_height = int(max(100, h * 0.2))
        status_x = w - status_width - 15
        status_y = h - status_height - 15
        
        # Draw status panel background
        cv2.rectangle(frame, (status_x, status_y), (w - 15, h - 15), (25, 25, 25), -1)
        cv2.rectangle(frame, (status_x, status_y), (w - 15, h - 15), (100, 100, 100), 2)
        
        if self.app_mode == "PAINTER":
            cv2.putText(frame, f"Mode: PAINTER - {self.mode}", (status_x + 15, status_y + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1)
            col_label = "ERASER" if self.is_eraser else self.color_names[self.selected_color_idx]
            cv2.putText(frame, f"Tool: {col_label}", (status_x + 15, status_y + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1)
            cv2.putText(frame, f"Brush Size: {self.brush_thickness}", (status_x + 15, status_y + 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            cv2.putText(frame, f"Canvas: {w}x{h}", (status_x + 15, status_y + 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
        else:
            cv2.putText(frame, f"Mode: CHEMISTRY - {self.mode}", (status_x + 15, status_y + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 1)
            cv2.putText(frame, f"Chemical: {self.selected_chemical[:12]}", (status_x + 15, status_y + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 1)
            if self.dragging_chemical:
                cv2.putText(frame, f"Dragging: {self.dragging_chemical[:12]}", (status_x + 15, status_y + 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 100), 1)
            else:
                active_reactions = len(self.chemistry_engine.active_reactions)
                cv2.putText(frame, f"Active Reactions: {active_reactions}", (status_x + 15, status_y + 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            cv2.putText(frame, f"Lab Size: {w}x{h}", (status_x + 15, status_y + 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)

        # Show finger detection in bottom left
        if detected_fingers is not None:
            finger_status = "".join(["1" if f else "0" for f in detected_fingers])
            cv2.putText(frame, f"Fingers: {finger_status}", (15, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

    def draw_smooth_line(self, img, start_pos, end_pos, color, thickness):
        if start_pos is None or end_pos is None:
            return
        x0, y0 = int(start_pos[0]), int(start_pos[1])
        x1, y1 = int(end_pos[0]), int(end_pos[1])
        dist = int(np.hypot(x1 - x0, y1 - y0))
        if dist == 0:
            cv2.circle(img, (x1, y1), thickness // 2, color, -1)
            return
        steps = max(1, dist // 2)
        for i in range(steps + 1):
            t = i / steps
            xi = int(x0 + (x1 - x0) * t)
            yi = int(y0 + (y1 - y0) * t)
            cv2.circle(img, (xi, yi), thickness // 2, color, -1)



    def run(self):
        print("🎨 FunDraw_ChemLab — AI Virtual Painter & Chemistry Lab (Press 'q' to quit)")
        
        # Local execution only
        if self.cam_index is None:
            self.cam_index = 0
            
        cap = cv2.VideoCapture(self.cam_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Set window to fullscreen for better utilization
        cv2.namedWindow("FunDraw_ChemLab - AI Virtual Painter & Chemistry Lab", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("FunDraw_ChemLab - AI Virtual Painter & Chemistry Lab", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        while True:
            success, frame = cap.read()
            if not success:
                print("Cannot read camera. Exiting.")
                break
            
            # process_frame handles flipping and logic
            # Note: process_frame flips input, but here we read raw which is usually not mirrored.
            # So process_frame flipping it will mirror it (good for selfie view).
            processed_frame = self.process_frame(frame)

            cv2.imshow("FunDraw_ChemLab - AI Virtual Painter & Chemistry Lab", processed_frame)

            # Key handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC to quit
                break
            elif key == ord('f'):  # Toggle fullscreen
                cv2.setWindowProperty("FunDraw_ChemLab - AI Virtual Painter & Chemistry Lab", 
                                    cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            elif key == ord('c') and self.app_mode == "PAINTER":
                self.canvas = np.zeros_like(self.canvas)
                print("[FunDraw_ChemLab] Canvas cleared.")
            elif key == ord('r') and self.app_mode == "CHEMISTRY":
                # Reset chemistry lab
                for beaker in self.beakers:
                    beaker["chemicals"] = []
                self.chemistry_engine.active_reactions = []
                self.canvas = np.zeros_like(self.canvas)
                print("[FunDraw_ChemLab] Chemistry lab reset.")
            elif key == ord('s'):
                self.save_canvas()
            elif key == ord('l'):
                # Toggle between modes
                self.app_mode = "CHEMISTRY" if self.app_mode == "PAINTER" else "PAINTER"
                self.canvas = np.zeros_like(self.canvas)
                print(f"[FunDraw_ChemLab] Switched to {self.app_mode} mode.")
            elif key == ord('+') or key == ord('='):
                if self.app_mode == "PAINTER":
                    self.brush_thickness = min(self.brush_thickness + 2, 60)
                    print(f"[FunDraw_ChemLab] Brush thickness: {self.brush_thickness}")
            elif key == ord('-') or key == ord('_'):
                if self.app_mode == "PAINTER":
                    self.brush_thickness = max(self.brush_thickness - 2, 2)
                    print(f"[FunDraw_ChemLab] Brush thickness: {self.brush_thickness}")
            elif key == ord('e') and self.app_mode == "PAINTER":
                self.is_eraser = not self.is_eraser
                print("[FunDraw_ChemLab] Eraser:", self.is_eraser)

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = RamperVirtualPainter()
    app.run()

'''
Index finger → Draw
Index + Middle → Select colors
C → Clear canvas
+/- → Brush size
S → Save painting

Chemistry Mode:

Two fingers → Select chemicals
Pinch & drag → Move chemicals
R → Reset lab (clear all beakers)
S → Save experiment

Global:

L → Toggle between modes
Q → Quit application


'''