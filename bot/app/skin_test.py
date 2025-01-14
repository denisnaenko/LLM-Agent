from collections import Counter

async def determine_skin_type(answers):
    """
    Асинхронная функция для определения типа кожи, особенностей и рисков на основе ответов пользователя.

    Args:
        answers (dict): Словарь ответов пользователя.

    Returns:
        tuple: (skin_type, features, risks)
    """
    # Определение типа кожи
    st_answers = []  # st -> skin type
    for i in range(1, 7):
        cur_st_answer = answers.get(f"answer_{i}")
        st_answers.append(cur_st_answer)

    ctr = Counter(st_answers)
    most_common_st_answer = ctr.most_common(1)[0][0]

    if most_common_st_answer == "a":
        skin_type = "Нормальная"
    elif most_common_st_answer == "b":
        skin_type = "Cухая"
    elif most_common_st_answer == "c":
        skin_type = "Жирная"
    elif most_common_st_answer == "d":
        skin_type = "Комбинированная"

    # Определение особенностей кожи
    features = []

    if answers.get("answer_8") == "c":
        features.append("акне редко")
    elif answers.get("answer_8") == "d":
        features.append("акне много")
    
    if answers.get("answer_9") == "a":
        features.append("постакне")

    if answers.get("answer_10") == "b":
        features.append("легкие морщины")
    elif answers.get("answer_10") == "c":
        features.append("неглубокие морщины")
    elif answers.get("answer_10") == "d":
        features.append("глубокие морщины")
    
    if answers.get("answer_11") == "b":
        features.append("краснота/купероз")
    
    if answers.get("answer_12") == "b":
        features.append("отечность")

    # Определение рисков для кожи
    risks = []

    if answers.get("answer_13") in ["b", "c"]:
        risks.append("беременность")

    return skin_type, features, risks
