require_relative "send2peer/command_loader"

module Send2Peer
  class CLI
    def run(args)
      command_name = args.shift
      command = Send2Peer::CommandLoader.load(command_name)
      command.execute(args)
    end
  end
end
