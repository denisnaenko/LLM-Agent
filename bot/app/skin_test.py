from collections import Counter

def determine_skin_type(answers):
    all_answers = []
    for i in range(1, 7):
        cur_answer = answers.get(f"answer_{i}")
        all_answers.append(cur_answer)
    
    ctr = Counter(all_answers)
    most_common_answer = ctr.most_common(1)[0][0]

    if most_common_answer == "a":
        return "Нормальная"
    elif most_common_answer == "b":
        return "Cухая"
    elif most_common_answer == "c":
        return "Жирная"
    elif most_common_answer == "d":
        return "Комбинированная"