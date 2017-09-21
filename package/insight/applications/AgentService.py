from insight.agent import AgentService


def main():
    agent = AgentService()
    agent.start()
    agent.join()


if __name__ == "__main__":
    main()
