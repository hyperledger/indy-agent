from message import Message


class Module():
    PROBLEM_REPORT = 'problem_report'

    @staticmethod
    def build_problem_report_for_connections(family, problem_code, problem_str):
        return Message({
            "@type": "{}/problem_report".format(family),
            "problem-code": problem_code,
            "explain": problem_str
        })
