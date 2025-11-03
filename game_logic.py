import random

suits = ('Hearts', 'Diamonds', 'Spades', 'Clubs')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')
values = {'Two':2, 'Three':3, 'Four':4, 'Five':5, 'Six':6, 'Seven':7, 'Eight':8, 'Nine':9, 'Ten':10, 'Jack':10, 'Queen':10, 'King':10, 'Ace':11}



class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = values[rank]

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class Deck:

    def __init__(self):
        self.deck = [Card(suit, rank) for suit in suits for rank in ranks]
    
    def shuffle(self):
        random.shuffle(self.deck)
    
    def deal(self):
        return self.deck.pop()


class Hand:
    
    def __init__(self):
        self.hand = []
        self.cards = []
        self.value = 0
        
    def add_cards(self,card):
        if card.rank == 'Ace':
            print("You drew an Ace!")
            print(f"Here is your hand so far: {self.cards}")
            print()
            try:
                card.value = int(input("Choose what value you want your Ace-ranked card to have (1 or 11): "))
            except:
                print("That is not a valid value.")
            while card.value not in [1, 11]:
                try:
                    card.value = int(input("Choose what value you want your Ace-ranked card to have (1 or 11): "))
                except:
                    print("That is not a valid value.")
            print()
        self.value += card.value
        self.hand.append(card)
        self.cards = [card.__str__() for card in self.hand]
        self.cards = ', '.join(self.cards)

    def deal_cards(self, card):
        if card.rank == 'Ace':
            if self.value + 11 > 21:
                card.value = 1
            else:
                card.value = 11
        self.value += card.value
        self.hand.append(card)
        self.cards = [card.__str__() for card in self.hand]
        self.cards = ', '.join(self.cards)

    def __str__(self):
        return self.cards


class Chips:
    
    def __init__(self):
        self.total = 100
        self.bet = 0

    def win_bet(self):
        self.total += self.bet
    
    def lose_bet(self):
        self.total -= self.bet



def player_hit(hand):
    hand.add_cards(the_deck.deal())

def dealer_hit(hand):
    hand.deal_cards(the_deck.deal())


def double_down(chips):
    chips.bet = chips.bet * 2


def split(hand):

    hand1 = Hand()
    hand1.hand.append(hand.hand[0])
    hand1.cards.append(hand.cards[0])
    hand1.value = hand.hand[0].value
    hand2 = Hand()
    hand2.hand.append(hand.hand[1])
    hand2.cards.append(hand.cards[1])
    hand2.value = hand.hand[1].value
    
    print("You chose to split your hand.")
    print(f"Your first hand: {hand1.cards}; value: {hand1.value}")
    print(f"Your second hand: {hand2.cards}; value: {hand2.value}")

    return hand1, hand2

def insurance(chips):
    bet = chips.bet / 2
    return bet

def show_hands(hand1, hand2):
    print(f"Your hand: {hand1.cards}; value: {hand1.value}")
    print(f"Dealer's hand: {hand2.hand[0]}, hole")

def reveal_hands(player_hand, dealer_hand):
    print(f"Your hand: {player_hand.cards}; value: {player_hand.value}")
    print(f"Dealer's hand: {dealer_hand.cards}; value: {dealer_hand.value}")

def deal_hands(deck):
    player_hand = Hand()
    dealer_hand = Hand()
    player_hand.add_cards(deck.deal())
    player_hand.add_cards(deck.deal())
    dealer_hand.deal_cards(deck.deal())
    dealer_hand.deal_cards(deck.deal())
    return player_hand, dealer_hand

def player_wins(player_hand, dealer_hand):
    if player_hand.value > dealer_hand.value:
        print("You got a higher value! You win!")
        return True
    else: return False

def dealer_wins(dealer_hand, player_hand):
    if dealer_hand.value > player_hand.value:
        print("Dealer got a higher value. Dealer wins.")
        return True
    else: return False

def break_even(player_hand, dealer_hand):
    if player_hand.value == dealer_hand.value:
        print("It's a tie! You break even.")
        return True
    else: return False

def blackjack_check(hand):
    if hand.value == 21 and len(hand.hand) == 2:
        print("Blackjack!")
        return True
    return False

def insurance_win(bet, chips):
    chips.total += bet / 2
    print(f"You won the insurance bet! You now have {chips.total} chips.")

def take_bet(chips):
    while True:
        try:
            bet = int(input("How much do you want to bet? "))
            if bet > chips.total:
                print(f"You cannot bet more than you have ({chips.total} chips).")
            elif bet <= 0:
                print("You must bet a positive amount.")
            else:
                chips.bet = bet
                break  # Valid bet accepted
        except ValueError:
            print("That is not a valid integer.")

def bust_check(player_hand):
    if player_hand.value > 21:
        return True
    return False

def surrender(chips):
    chips.total -= chips.bet / 2
    print(f"You surrendered. You lost half your bet. You now have {chips.total} chips.")
    return False  # End the game after surrendering



# Only run this if the script is executed directly (not imported by the GUI)
if __name__ == "__main__":
    playing = True
    player_chips = Chips()
    while playing:

        print()
        print("Welcome to Blackjack!")
        print("You are the player and the computer is the dealer.")
        print()

        the_deck = Deck()
        the_deck.shuffle()
        print("Shuffling the deck...")
        print()

        print(f"You have {player_chips.total} chips.")
        take_bet(player_chips)
        print()

        player_hand, dealer_hand = deal_hands(the_deck)
        print("Dealing cards...")
        show_hands(player_hand, dealer_hand)
        bust_check(player_hand)
        print()

        run = True
        while run:
            player_turn = True
            while player_turn:
                choice = input("What do you want to do: hit, stand, double down, split, insurance, surrender? ").strip().lower()
                while choice not in ['hit', 'stand', 'double down', 'split', 'insurance', 'surrender']:
                    print("That is not an option.")
                    choice = input("What do you want to do: hit, stand, double down, split, insurance, surrender? ")
                print()
                if choice == 'hit':
                    player_hit(player_hand)
                    print(f"You received a {player_hand.cards.split(', ')[-1]}.")
                    print()
                    if bust_check(player_hand):
                        player_chips.lose_bet()
                        show_hands(player_hand, dealer_hand)
                        print()
                        print(f"You lost your bet of {player_chips.bet}. You now have {player_chips.total} chips.")
                        print()
                        player_turn = False
                        run = False
                        break
                elif choice == 'double down':
                    if player_chips.total < player_chips.bet * 2:
                        print("You do not have enough chips to double down.")
                    else:
                        double_down(player_chips)
                        player_hit(player_hand)
                        print(f"You received a {player_hand.cards.split(', ')[-1]}.")
                        print()
                        if bust_check(player_hand):
                            player_chips.lose_bet()
                            show_hands(player_hand, dealer_hand)
                            print()
                            print(f"You lost your bet of {player_chips.bet}. You now have {player_chips.total} chips.")
                            print()
                            player_turn = False
                            run = False
                            break
                        else:
                            print(f"You doubled down and now have {player_chips.total} chips.")
                            player_turn = False
                elif choice == 'split':
                    if len(player_hand.hand) != 2 or player_hand.hand[0].value != player_hand.hand[1].value:
                        print("You can only split if you have two cards of the same value.")
                    else:
                        player_hand1, player_hand2 = split(player_hand)
                        print("You now have two hands to play.")
                        show_hands(player_hand1, dealer_hand)
                        print()
                        show_hands(player_hand2, dealer_hand)
                        print()
                        # Now handle each hand separately
                        hand1_turn = True
                        while hand1_turn:
                            choice1 = input("What do you want to do with your first hand, hit or stand? ").strip().lower()
                            while choice1 not in ['hit', 'stand']:
                                print("That is not an option.")
                                choice1 = input("What do you want to do with your first hand, hit or stand? ")
                            if choice1 == 'hit':
                                player_hit(player_hand1)
                                print(f"You received a {player_hand1.cards.split(', ')[-1]}.")
                                if bust_check(player_hand1):
                                    player_chips.lose_bet()
                                    show_hands(player_hand1, dealer_hand)
                                    print()
                                    print(f"You lost your bet of {player_chips.bet}. You now have {player_chips.total} chips.")
                                    hand1_turn = False
                            elif choice1 == 'stand':
                                print("You chose to stand with your first hand.")
                                hand1_turn = False
                        hand2_turn = True
                        while hand2_turn:
                            choice2 = input("What do you want to do with your second hand, hit or stand? ").strip().lower()
                            while choice2 not in ['hit', 'stand']:
                                print("That is not an option.")
                                choice2 = input("What do you want to do with your second hand, hit or stand? ")
                            if choice2 == 'hit':
                                player_hit(player_hand2)
                                print(f"You received a {player_hand2.cards.split(', ')[-1]}.")
                                if bust_check(player_hand2):
                                    player_chips.lose_bet()
                                    show_hands(player_hand2, dealer_hand)
                                    print()
                                    print(f"You lost your bet of {player_chips.bet}. You now have {player_chips.total} chips.")
                                    hand2_turn = False
                            elif choice2 == 'stand':
                                print("You chose to stand with your second hand.")
                                hand2_turn = False
                elif choice == 'insurance':
                    if dealer_hand.hand[0].rank == 'Ace':
                        insurance_bet = insurance(player_chips)
                        print(f"You placed an insurance bet of {insurance_bet}.")
                        if blackjack_check(dealer_hand):
                            insurance_win(insurance_bet, player_chips)
                        else:
                            print("The dealer does not have a blackjack. You lost your insurance bet.")
                            player_chips.total -= insurance_bet
                    else:
                        print("You can only place an insurance bet if the dealer's face-up card is an Ace.")
                elif choice == 'surrender':
                    run = surrender(player_chips)
                    if not run:
                        print("You surrendered. The game is over.")
                        break
                elif choice == 'stand':
                    print("You chose to stand. The dealer will now play.")
                    print()
                    player_turn = False
                show_hands(player_hand, dealer_hand)
                print()

            if not run:
                break   

            while dealer_hand.value < 17:
                dealer_hit(dealer_hand)
                print(f"The dealer received a {dealer_hand.cards.split(', ')[-1]}.")
                print()
                reveal_hands(player_hand, dealer_hand)
                print()
                if bust_check(dealer_hand):
                    player_chips.win_bet()
                    print(f"The dealer busts! You won your bet of {player_chips.bet}! You now have {player_chips.total} chips.")
                    print()
                    run = False
                    break

            if not run:
                break
        
            reveal_hands(player_hand, dealer_hand)
            print()
            if player_wins(player_hand, dealer_hand):
                player_chips.win_bet()
                run = False
                print(f"Here's your winnings: You gained {player_chips.bet} and now have {player_chips.total} chips!")
            elif dealer_wins(dealer_hand, player_hand):
                player_chips.lose_bet()
                run = False
                print(f"You lost your bet. You lost {player_chips.bet} now have {player_chips.total} chips.")
            elif break_even(player_hand, dealer_hand):
                print("You break even. You did not win or lose any chips.")
                run = False
            print()

        print(f"You have {player_chips.total} chips left.")
        print()
        play_again = input("Do you want to play again? (yes or no): ").strip().lower()
        while play_again not in ['yes', 'no']:
            play_again = input("Do you want to play again? (yes or no): ").strip().lower()
        if play_again == 'yes':
            playing = True
        else:
            playing = False
        print()

    print("You ended the game with", player_chips.total, "chips.")
    print("Thanks for playing! Goodbye!")
    print()