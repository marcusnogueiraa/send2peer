require 'optparse'

module Send2Peer
  module Commands
    class VersionCommand
      HELP_BANNER = <<~HELP
        Usage: send2peer version
        
        Displays the current version of the send2peer CLI tool.
      HELP

      def execute(args)

        if args.include?("--help")
          puts HELP_BANNER
          return
        end

        puts "📦 send2peer v#{Send2Peer::VERSION}"
      end
    end
  end
end