import cmd
from prettytable import PrettyTable
from insight.storage import DBJobInstance


class InsightCLI(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "Insight >> "

    def do_exit(self, args):
        exit()

    def do_new(self, args):
        params = self._extract_parameters(args)
        job = DBJobInstance()
        job.new_job({
            
        })
        print(self._extract_parameters(args))

    def _extract_parameters(self, args):
        params = {}
        args_array = args.split(' ')
        for a in args_array:
            group = a.split("=")
            if len(group) == 2:
                params[group[0]] = group[1]
        return params


if __name__ == "__main__":
    InsightCLI().cmdloop()
