import random
from playcard import make_deck

# 牌面点数映射
CARD_VALUES = {
    'A': 11,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'T': 10,
    'J': 10,
    'Q': 10,
    'K': 10,
}

def calculate_hand_value(hand):
    """计算手牌点数，自动处理A(11/1)"""
    value, aces = 0, 0
    for card in hand:
        rank = card[0]
        value += CARD_VALUES[rank]
        aces += rank == 'A'
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def is_natural_blackjack(hand):
    """判断是否为天然Blackjack：仅2张牌，A + 10点牌"""
    if len(hand) != 2:
        return False
    r1, r2 = hand[0][0], hand[1][0]
    ten_ranks = {'T', 'J', 'Q', 'K'}
    return (r1 == 'A' and r2 in ten_ranks) or (r2 == 'A' and r1 in ten_ranks)

def new_game(session):
    """欧版开局：庄家只发1张明牌，暗牌单独存储，不提前判BJ"""
    deck = make_deck()
    random.shuffle(deck)
    c1, c2, c3, c4 = deck.pop(), deck.pop(), deck.pop(), deck.pop()

    player_hand = [c1, c3]
    dealer_hand = [c2]
    dealer_hidden_card = c4

    dealer_value = calculate_hand_value(dealer_hand)
    player_value = calculate_hand_value(player_hand)

    message = None
    message_class = ""

    session['game_state'] = {
        'deck': deck,
        'dealer_hand': dealer_hand,
        'dealer_hidden_card': dealer_hidden_card,
        'player_hand': player_hand,
        'dealer_value': dealer_value,
        'player_value': player_value,
        'message': message,
        'message_class': message_class,
    }

def game_update(session, action):
    game_state = session.get('game_state', {})
    if not game_state:
        return new_game(session)

    deck = game_state['deck']
    dealer_hand = game_state['dealer_hand']
    dealer_hidden_card = game_state['dealer_hidden_card']
    player_hand = game_state['player_hand']

    if action == 'hit':
        # 玩家要牌
        card = deck.pop()
        player_hand.append(card)
        player_val = calculate_hand_value(player_hand)
        game_state['player_value'] = player_val
        # 玩家爆牌
        if player_val > 21:
            game_state['dealer_value'] = calculate_hand_value(dealer_hand)
            game_state['message'] = 'You busted! Dealer wins.'
            game_state['message_class'] = 'lose-message'

    elif action == 'stand':
        # 玩家停牌：庄家补齐第二张牌
        dealer_hand.append(dealer_hidden_card)
        player_val = game_state['player_value']
        dealer_val = calculate_hand_value(dealer_hand)

        # 欧版核心：判断天然Blackjack
        dealer_bj = is_natural_blackjack(dealer_hand)
        player_bj = is_natural_blackjack(player_hand)

        if dealer_bj:
            if player_bj:
                game_state['message'] = "Double natural Blackjack! It's a tie!"
                game_state['message_class'] = 'tie-message'
            else:
                game_state['message'] = "Dealer has natural Blackjack! Dealer wins!"
                game_state['message_class'] = 'lose-message'
        else:
            # 庄家点数小于17继续要牌
            while dealer_val < 17:
                new_card = deck.pop()
                dealer_hand.append(new_card)
                dealer_val = calculate_hand_value(dealer_hand)
            game_state['dealer_value'] = dealer_val

            # 常规胜负判断
            if dealer_val > 21:
                game_state['message'] = 'Dealer busted! You win!'
                game_state['message_class'] = 'win-message'
            elif dealer_val > player_val:
                game_state['message'] = 'Dealer wins!'
                game_state['message_class'] = 'lose-message'
            elif dealer_val < player_val:
                game_state['message'] = 'You win!'
                game_state['message_class'] = 'win-message'
            else:
                game_state['message'] = "It's a tie!"
                game_state['message_class'] = 'tie-message'

    session.modified = True