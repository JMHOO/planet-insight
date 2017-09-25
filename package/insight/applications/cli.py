import cmd
from datetime import datetime
from prettytable import PrettyTable
from insight.storage import DBJobInstance, DBInstanceLog, DBInsightModels, S3DB
from simple_settings import LazySettings
from decimal import Decimal
import json
import os
from pygments import highlight, lexers, formatters


settings = LazySettings('insight.applications.settings')

class InsightCLI(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self._jobs = DBJobInstance()
        self._models = DBInsightModels()
        self.prompt = "Insight >> "

    def do_exit(self, args):
        exit()

    def do_newjob(self, args):
        params = self._extract_parameters(args)
        if self._check_parameters(params, ['name', 'model', 'data', 'epochs']):
            if 'weights' in params:
                weights = params["weights"]
            else:
                weights = "NONE"

            self._jobs.new_job({
                "job_status": "initial",
                "instance_name": params["name"],
                "model_name": params["model"],
                "dataset_name": params["data"],
                "pretrain": weights,
                "epochs": params["epochs"]
            })

    def do_jobs(self, args):
        all_job = self._jobs.list()
        resTable = PrettyTable(["#", "Name", "Model", "Dataset", "Status", "Created"])
        resTable.align["Name"] = "l"
        resTable.align["Dataset"] = "l"
        resTable.padding_width = 1

        for index, (j) in enumerate(all_job):
            timestamp = datetime.fromtimestamp(float(j['created']))
            timestamp = timestamp.strftime('%Y-%m-%d %H:%m')
            resTable.add_row([index + 1, j['instance_name'], j['model_name'], j['dataset_name'], j['job_status'], timestamp])

        print(resTable)

    def do_models(self, args):
        all_models = self._models.list()
        resTable = PrettyTable(["#", "Name", "JSON"])
        resTable.align["Name"] = "l"
        resTable.align["JSON"] = "l"
        resTable.padding_width = 1

        for index, item in enumerate(all_models):
            model_def = item["model_defination"][:100] + "..."
            resTable.add_row([index + 1, item["model_name"], model_def])

        print(resTable)

    def do_model(self, args):
        model_name = args
        json_model = self._models.get(model_name)
        colorful_json = highlight(json_model, lexers.JsonLexer(), formatters.TerminalFormatter())
        print(colorful_json)

    def do_newmodel(self, args):
        params = self._extract_parameters(args)
        if self._check_parameters(params, ['name', 'json']):
            if os.path.exists(params['json']):
                with open(params['json'], 'r') as fp:
                    json_content = json.load(fp)
                    db_model = DBInsightModels()
                    db_model.put(params['name'], json.dumps(json_content))

    def do_results(self, args):
        resTable = PrettyTable(["#", "Name", "Size"])
        resTable.align["Name"] = "l"
        resTable.align["Size"] = "l"
        resTable.padding_width = 1

        s3_models = S3DB(bucket_name=settings.S3_BUCKET['RESULTS'])
        all_file = s3_models.list()
        for index, f in enumerate(all_file):
            resTable.add_row([index + 1, f['name'], f['size']])
        print(resTable)

    def do_logs(self, args):
        instance_name = args
        resTable = PrettyTable(["#", "Message"])
        resTable.align["Message"] = "l"
        resTable.padding_width = 1

        db_log = DBInstanceLog(instance_name)
        logs = db_log.fetch()
        for index, l in enumerate(logs):
            message = l.get("info", None)
            if message is None:
                message = l.get("train", None)
                if message:
                    loss = message.get('loss', '')
                    if loss:
                        loss = 'LOSS: {:.5f} '.format(loss)
                    val_loss = message.get('val_loss', '')
                    if val_loss:
                        val_loss = 'VAL LOSS: {:.5f} '.format(val_loss)
                    acc = message.get('acc', '')
                    if acc:
                        acc = 'Accuracy: {:.5f} '.format(acc)
                    val_acc = message.get('val_acc', '')
                    if val_acc:
                        val_acc = 'VAL Accuracy: {:.5f} '.format(val_acc)
                    message = 'Epoch-{:02d} '.format(message['epoch']) + acc + val_acc + loss + val_loss

            if message:
                message = message[:80] + '...'
                resTable.add_row([index + 1, message])

        print(resTable)

    def _extract_parameters(self, args):
        params = {}
        args_array = args.split(' ')
        for a in args_array:
            group = a.split("=")
            if len(group) == 2:
                params[group[0]] = group[1]
        return params

    def _check_parameters(self, params, check_list):
        for c in check_list:
            if c not in params:
                print("Parameter error, missing: {}".format(c))
                return False
        return True


if __name__ == "__main__":
    InsightCLI().cmdloop()
