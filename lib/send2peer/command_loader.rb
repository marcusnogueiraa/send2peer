require_relative "version"
require_relative "commands/version_command.rb"

module Send2Peer
  class CommandLoader
    def self.load(command_name)
      {
        "version" => Commands::VersionCommand.new
      }[command_name]
    end
  end
end