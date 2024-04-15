

from utils.evaluation import eval_model, eval_model_function, evaluate_re_rank_func, evaluation, evaluation_summary, eval_model_function_parrallel


# evaluation()
if __name__ == "__main__":
    result_file = 'evaluation_results_function_1-100_big_top100.json'
    # eval_model_function('../maven_repos/', result_file, 0, 90)
    eval_model_function_parrallel(result_file, 'evaluation_results_function_1-100_small_top100', 0, 100)
    # evaluation_summary(['evaluation_results_function_1-100.json', 'evaluation_results_function_1-100-2.json'])
    # evaluation_summary()
    # evaluate_re_rank_func()
