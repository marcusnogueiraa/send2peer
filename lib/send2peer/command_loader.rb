require_relative 'version'
require_relative 'commands/version_command.rb'
require_relative 'commands/ip_command.rb'

module Send2Peer
  class CommandLoader

    def self.load(command_name)
      {
        "version" => Commands::VersionCommand.new,
        "ip" => Commands::IpCommand.new
      }[command_name]
    end
  end
end