from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QPushButton, QLineEdit, QInputDialog, QLayout, QSizePolicy
from PySide6.QtCore import Qt, QRect, QSize, QPoint
from PySide6.QtGui import QPixmap
import game_logic


class FlowLayout(QLayout):
    """
    Custom layout that arranges widgets in a horizontal flow, wrapping to new lines as needed.
    Used for displaying card images in a row for both player and dealer hands.
    """
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing
        self.itemList = []

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        """
        Internal layout logic: positions widgets left-to-right, wrapping to new lines as needed.
        """
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        effective_spacing = self.spacing()
        if effective_spacing == -1:
            effective_spacing = 6

        for item in self.itemList:
            wid = item.widget()
            spaceX = effective_spacing
            spaceY = effective_spacing
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


class BlackjackGUI(QMainWindow):
    """
    Main GUI window for the Blackjack game.
    Handles all user interactions, card display, and round/bet/game flow.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blackjack")
        self.setStyleSheet("background-color: green;")
        self.setFixedSize(1000, 600)

        # --- Game State ---
        self.player_chips = game_logic.Chips()
        self.summary_shown = False
        self.deck = None
        self.player_hand = None
        self.dealer_hand = None
        self.hide_dealer_first_card = True  # Used to hide dealer's first card until round end

        # --- GUI Widgets ---
        self.player_bet_label = QLabel("Your Bet :  ")
        self.player_chips_label = QLabel(f"Your Chips:  {self.player_chips.total}")

        # --- Card Image Preloading ---
        # Preload and pre-scale all card images for efficient display.
        # Card images are stored in self.card_pixmaps for quick lookup.
        self.card_pixmaps = {}
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        suits = ['hearts', 'diamonds', 'spades', 'clubs']
        for suit in suits:
            for rank in ranks:
                card_name = f"{rank}_of_{suit}"
                path = f"PNG-cards/{card_name}.png"
                pixmap = QPixmap(path).scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.card_pixmaps[card_name] = pixmap
        # Load card back image
        back_card_path = "PNG-cards/card back black.png"
        self.card_pixmaps["back"] = QPixmap(back_card_path).scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # --- Show Rules/Intro ---
        rules_intro = QMessageBox()
        rules_intro.setWindowTitle("How to Play")
        rules_intro.setText("Welcome to Blackjack! The goal is to get as close to 21 as possible without going over. Good luck!")
        rules_intro.setStandardButtons(QMessageBox.Ok)
        # Set custom info icon (now using game.png)
        rules_intro.setIconPixmap(QPixmap("game.png").scaled(64, 64, Qt.KeepAspectRatio))
        rules_intro.setStyleSheet("background-color: lightblue; color: black;")
        rules_intro.exec()

        # Prompt for initial bet before first round
        self.take_bet()

        # --- Build GUI Layout ---
        # Main labels for hands
        self.dealer_hand_label = QLabel("Dealer's Hand :  ")
        self.player_hand_label = QLabel("Your Hand :  ")

        # Action buttons (Hit, Stand)
        options_label = QLabel("What would you like to do?")
        button_hit = QPushButton("Hit")
        button_hit.setFixedHeight(100)
        button_hit.clicked.connect(self.hit)
        button_stand = QPushButton("Stand")
        button_stand.setFixedHeight(100)
        button_stand.clicked.connect(self.stand)
        # Removed buttons for double down, split, insurance, surrender (not implemented)

        # Placeholder for deck image or future features (currently unused)
        deck_layout = QVBoxLayout()

        # --- Options Layout ---
        options_layout = QVBoxLayout()
        options_layout.addWidget(options_label)
        options_layout.addWidget(button_hit)
        options_layout.addWidget(button_stand)

        # --- Dealer Hand Layout ---
        dealer_layout = QVBoxLayout()
        dealer_layout.addWidget(self.dealer_hand_label)
        # Card container: uses FlowLayout to display dealer's cards in a row
        self.dealer_cards_widget = QWidget()
        self.dealer_cards_layout = FlowLayout()
        self.dealer_cards_layout.setSpacing(0)
        self.dealer_cards_widget.setLayout(self.dealer_cards_layout)
        dealer_layout.addWidget(self.dealer_cards_widget)
        dealer_layout.addStretch()

        # --- Player Hand Layout ---
        player_layout = QVBoxLayout()
        player_layout.addWidget(self.player_hand_label)
        # Card container: uses FlowLayout to display player's cards in a row
        self.player_cards_widget = QWidget()
        self.player_cards_layout = FlowLayout()
        self.player_cards_layout.setSpacing(0)
        self.player_cards_widget.setLayout(self.player_cards_layout)
        player_layout.addWidget(self.player_cards_widget)
        player_layout.addStretch()
        player_layout.addWidget(self.player_bet_label)
        player_layout.addWidget(self.player_chips_label)

        # --- Compose Main Layouts ---
        deck_and_options_layout = QHBoxLayout()
        deck_and_options_layout.addLayout(deck_layout)
        deck_and_options_layout.addLayout(options_layout)

        hands_layout = QHBoxLayout()
        hands_layout.addLayout(dealer_layout)
        hands_layout.addLayout(player_layout)

        layout = QVBoxLayout()
        layout.addLayout(deck_and_options_layout)
        layout.addLayout(hands_layout)

        # Set central widget and layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Delay start of first round until GUI is ready
        from PySide6.QtCore import QTimer
        QTimer.singleShot(200, self.start_new_round)

    def gui_deal_hands(self):
        """
        Deals initial two cards to both player and dealer.
        - For player: prompts for Ace value (1 or 11) using input dialog.
        - For dealer: chooses Ace value (11 if it doesn't bust, else 1).
        Returns: (player_hand, dealer_hand) as Hand objects.
        """
        player_hand = game_logic.Hand()
        dealer_hand = game_logic.Hand()

        # Deal two cards to player (prompt for Aces)
        for _ in range(2):
            card = self.deck.deal()
            if card.rank == 'Ace':
                # Prompt player to choose Ace value (1 or 11)
                ace_value, ok = QInputDialog.getInt(self, "Ace Value", "Choose value for Ace (1 or 11):", 11, 1, 11)
                if not ok or ace_value not in (1, 11):
                    ace_value = 11
                card.value = ace_value
            player_hand.hand.append(card)
            player_hand.value += card.value
        player_hand.cards = ', '.join(str(c) for c in player_hand.hand)

        # Deal two cards to dealer (automatic Ace logic)
        for _ in range(2):
            card = self.deck.deal()
            if card.rank == 'Ace':
                # Dealer chooses 11 if it doesn't bust, else 1
                if dealer_hand.value + 11 <= 21:
                    card.value = 11
                else:
                    card.value = 1
            dealer_hand.hand.append(card)
            dealer_hand.value += card.value
        dealer_hand.cards = ', '.join(str(c) for c in dealer_hand.hand)

        return player_hand, dealer_hand

    def update_card_images(self):
        """
        Updates the displayed card images for both player and dealer hands.
        Uses FlowLayout containers to arrange cards in a row.
        Handles hiding the dealer's first card until the round is over.
        """
        # Helper to clear all widgets from a layout
        def clear_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
                        widget.deleteLater()

        # Clear previous card images before updating
        clear_layout(self.dealer_cards_layout)
        clear_layout(self.player_cards_layout)

        # Normalize card rank names for image lookup
        rank_map = {
            'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5', 'Six': '6',
            'Seven': '7', 'Eight': '8', 'Nine': '9', 'Ten': '10',
            'Jack': 'jack', 'Queen': 'queen', 'King': 'king', 'Ace': 'ace'
        }

        # --- Dealer cards ---
        for i, card in enumerate(self.dealer_hand.hand):
            label = QLabel()
            label.setFixedSize(100, 145)
            # Hide dealer's first card if still in round
            if i == 1 and self.hide_dealer_first_card:
                pixmap = self.card_pixmaps.get("back")
            else:
                rank_key = rank_map.get(card.rank, card.rank.lower())
                suit_key = card.suit.lower()
                card_key = f"{rank_key}_of_{suit_key}"
                pixmap = self.card_pixmaps.get(card_key, self.card_pixmaps.get("back"))
            pixmap = pixmap.scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.dealer_cards_layout.addWidget(label)

        # --- Player cards ---
        for card in self.player_hand.hand:
            label = QLabel()
            label.setFixedSize(100, 145)
            rank_key = rank_map.get(card.rank, card.rank.lower())
            suit_key = card.suit.lower()
            card_key = f"{rank_key}_of_{suit_key}"
            pixmap = self.card_pixmaps.get(card_key, self.card_pixmaps.get("back"))
            pixmap = pixmap.scaled(100, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.player_cards_layout.addWidget(label)

        # Force layout update to fix overlay/glitch issues
        QApplication.processEvents()

    def update_bet_display(self):
        """Update the bet label to reflect the player's current bet."""
        self.player_bet_label.setText(f"Your Bet:  {self.player_chips.bet}")

    def update_chips_display(self):
        """Update the chips label to reflect the player's current chip count."""
        self.player_chips_label.setText(f"Your Chips:  {self.player_chips.total}")

    def check_out_of_chips(self):
        """
        Check if the player is out of chips.
        If so, show a message and end the game.
        Returns True if out of chips, else False.
        """
        if self.player_chips.total <= 0:
            # Custom icon for out of chips/game over
            mb = QMessageBox(self)
            mb.setWindowTitle("Out of Chips")
            mb.setText("You have no chips left to bet. Game over!")
            mb.setIconPixmap(QPixmap("empty-wallet.png").scaled(64, 64, Qt.KeepAspectRatio))
            mb.exec()
            self.show_game_summary()
            QApplication.quit()
            return True
        return False

    def take_bet(self):
        """
        Prompt the player to place a bet for the round.
        Ensures bet is between 1 and player's available chips.
        """
        if self.check_out_of_chips():
            return
        while True:
            bet, ok = QInputDialog.getInt(self, "Place your bet", f"Enter your bet (You have {self.player_chips.total} chips to bet):", 1, 1, self.player_chips.total)
            if not ok:
                mb = QMessageBox(self)
                mb.setWindowTitle("Bet Required")
                mb.setText("You must place a bet to play.")
                mb.setIconPixmap(QPixmap("red-x.png").scaled(64, 64, Qt.KeepAspectRatio))
                mb.exec()
                continue
            if bet < 1 or bet > self.player_chips.total:
                mb = QMessageBox(self)
                mb.setWindowTitle("Invalid Bet")
                mb.setText(f"Bet must be between 1 and {self.player_chips.total}.")
                mb.setIconPixmap(QPixmap("red-x.png").scaled(64, 64, Qt.KeepAspectRatio))
                mb.exec()
                continue
            self.player_chips.bet = bet
            self.update_bet_display()
            mb = QMessageBox(self)
            mb.setWindowTitle("Bet Placed")
            mb.setText(f"You bet {bet} chips.")
            mb.setIconPixmap(QPixmap("chips.png").scaled(64, 64, Qt.KeepAspectRatio))
            mb.exec()
            break

    def start_new_round(self):
        """
        Starts a new round:
        - Checks for chips
        - Shuffles a new deck
        - Deals hands
        - Updates GUI
        - Handles immediate blackjack win
        """
        if self.check_out_of_chips():
            return

        # Create and shuffle a new deck for each round
        self.deck = game_logic.Deck()
        self.deck.shuffle()

        # Deal hands (see gui_deal_hands for Ace handling logic)
        self.player_hand, self.dealer_hand = self.gui_deal_hands()

        self.hide_dealer_first_card = True

        # Update GUI labels to show initial cards
        self.dealer_hand_label.setText(f"Dealer's Hand: {self.dealer_hand.hand[0]} and [Hidden]")
        self.player_hand_label.setText(f"Your Hand: {self.player_hand.cards} (Value: {self.player_hand.value})")

        self.update_card_images()

        # Immediate win if player has blackjack (21 on deal)
        if self.player_hand.value == 21:
            mb = QMessageBox(self)
            mb.setWindowTitle("Blackjack!")
            mb.setText("Blackjack! You win 1.5x your bet!")
            mb.setIconPixmap(QPixmap("trophy.png").scaled(64, 64, Qt.KeepAspectRatio))
            mb.exec()
            self.player_chips.total += int(self.player_chips.bet * 1.5)
            self.update_chips_display()
            if self.ask_play_again():
                self.take_bet()
                self.start_new_round()
            else:
                self.show_game_summary()

    def hit(self):
        """
        Handles the 'Hit' action:
        - Deals a card to the player (prompts for Ace value)
        - Updates hand value and images
        - Checks for bust and handles round end if necessary
        """
        card = self.deck.deal()
        if card.rank == 'Ace':
            # Prompt player for Ace value on hit
            ace_icon = QPixmap("choice.png").scaled(64, 64, Qt.KeepAspectRatio)
            ace_value, ok = QInputDialog.getInt(self, "Ace Value", "Choose value for Ace (1 or 11):", 11, 1, 11)
            # Note: QInputDialog does not support icon, but we load the icon for possible future use.
            if not ok or ace_value not in (1, 11):
                ace_value = 11
            card.value = ace_value
        self.player_hand.hand.append(card)
        self.player_hand.value += card.value
        self.player_hand.cards = ', '.join(str(c) for c in self.player_hand.hand)
        self.player_hand_label.setText(f"Your Hand: {self.player_hand.cards} (Value: {self.player_hand.value})")
        self.update_card_images()

        # Bust check: if player goes over 21, round ends
        if self.player_hand.value > 21:
            mb = QMessageBox(self)
            mb.setWindowTitle("Bust")
            mb.setText(f"You busted with {self.player_hand.value}! You lose your bet of {self.player_chips.bet} chips.")
            mb.setIconPixmap(QPixmap("red-x.png").scaled(64, 64, Qt.KeepAspectRatio))
            mb.exec()
            self.player_chips.lose_bet()
            self.update_chips_display()
            if not self.check_out_of_chips() and self.ask_play_again():
                self.take_bet()
                self.start_new_round()
            elif self.check_out_of_chips():
                return
            else:
                self.show_game_summary()

    def stand(self):
        """
        Handles the 'Stand' action:
        - Dealer draws cards until value >= 17 (Aces handled automatically)
        - Reveals all dealer cards and updates GUI
        - Calls round resolution logic
        """
        # Dealer draws until hand value is at least 17
        while self.dealer_hand.value < 17:
            card = self.deck.deal()
            if card.rank == 'Ace':
                # Dealer logic: choose 11 if it doesn't bust, else 1
                if self.dealer_hand.value + 11 <= 21:
                    card.value = 11
                else:
                    card.value = 1
            self.dealer_hand.hand.append(card)
            self.dealer_hand.value += card.value
            self.dealer_hand.cards = ', '.join(str(c) for c in self.dealer_hand.hand)
        # Reveal all dealer cards and update GUI
        self.hide_dealer_first_card = False
        self.dealer_hand_label.setText(f"Dealer's Hand: {self.dealer_hand.cards} (Value: {self.dealer_hand.value})")
        self.update_card_images()
        self.resolve_round()

    def resolve_round(self):
        """
        Determines the outcome of the round (win, lose, push) and updates chips.
        Handles payout, shows outcome messages, and prompts for next round or summary.
        """
        player_val = self.player_hand.value
        dealer_val = self.dealer_hand.value
        bet = self.player_chips.bet

        # Dealer busts
        if dealer_val > 21:
            mb = QMessageBox(self)
            mb.setWindowTitle("Dealer Busts")
            mb.setText(f"Dealer busts with {dealer_val}! You win {bet} chips.")
            mb.setIconPixmap(QPixmap("trophy.png").scaled(64, 64, Qt.KeepAspectRatio))
            mb.exec()
            self.player_chips.win_bet()
        # Player wins
        elif player_val > dealer_val:
            mb = QMessageBox(self)
            mb.setWindowTitle("You Win")
            mb.setText(f"You win with {player_val} against dealer's {dealer_val}! You win {bet} chips.")
            mb.setIconPixmap(QPixmap("trophy.png").scaled(64, 64, Qt.KeepAspectRatio))
            mb.exec()
            self.player_chips.win_bet()
        # Player loses
        elif player_val < dealer_val:
            mb = QMessageBox(self)
            mb.setWindowTitle("You Lose")
            mb.setText(f"You lose with {player_val} against dealer's {dealer_val}. You lose {bet} chips.")
            mb.setIconPixmap(QPixmap("red-x.png").scaled(64, 64, Qt.KeepAspectRatio))
            mb.exec()
            self.player_chips.lose_bet()
        # Push (tie)
        else:
            mb = QMessageBox(self)
            mb.setWindowTitle("Push")
            mb.setText(f"It's a tie at {player_val}. Your bet is returned.")
            mb.setIconPixmap(QPixmap("neutral-icon.png").scaled(64, 64, Qt.KeepAspectRatio))
            mb.exec()

        self.update_chips_display()

        # Check for chips after round
        if self.check_out_of_chips():
            return

        # Ask if player wants to play another round (if chips remain)
        if self.ask_play_again():
            self.take_bet()
            self.start_new_round()
        else:
            self.show_game_summary()

    def ask_play_again(self):
        """
        Prompt the player to play another round.
        Returns True if Yes, False if No.
        """
        mb = QMessageBox(self)
        mb.setWindowTitle("Play Again?")
        mb.setText(f"You currently have {self.player_chips.total} chips. Do you want to play another round?")
        mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        mb.setIconPixmap(QPixmap("Information_icon.png").scaled(64, 64, Qt.KeepAspectRatio))
        reply = mb.exec()
        return reply == QMessageBox.Yes

    def show_game_summary(self):
        """
        Shows a summary of the player's results at the end of the game.
        Displays total chips and net winnings, then exits.
        """
        if self.summary_shown:
            return
        self.summary_shown = True
        summary_box = QMessageBox(self)
        summary_box.setWindowTitle("Game Summary")
        net_winnings = self.player_chips.total - 100
        summary_box.setText(f"Thank you for playing!\n\nTotal Chips: {self.player_chips.total}\nNet Winnings: {net_winnings}")
        summary_box.setStandardButtons(QMessageBox.Close)
        summary_box.setIconPixmap(QPixmap("game.png").scaled(64, 64, Qt.KeepAspectRatio))
        summary_box.exec()
        QApplication.quit()


if __name__ == "__main__":
    # Launch the Blackjack GUI application
    app = QApplication([])
    window = BlackjackGUI()
    window.show()
    app.exec()
