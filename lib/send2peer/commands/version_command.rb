module Send2Peer
  module Commands
    class VersionCommand
      def execute(args)
        puts "send2peer - " + VERSION
      end
    end
  end
end