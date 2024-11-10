def determine_skin_type(answers):
    answer_1 = answers.get("answer_1")
    answer_2 = answers.get("answer_2")
    answer_3 = answers.get("answer_3")

    if answer_1 == "a" and answer_2 == "a" and answer_3 == "b":
        return "Жирная кожа"
    elif answer_1 == "c" and answer_3 == "a":
        return "Сухая и чувствительная кожа"
    elif answer_2 == "b" and answer_3 == "b":
        return "Комбинированная кожа"
    else:
        return "Нормальная кожа"