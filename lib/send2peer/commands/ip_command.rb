require 'socket'
require 'net/http'
require 'uri'
require 'optparse'

module Send2Peer
  module Commands
    class IpCommand

      HELP_BANNER = <<~HELP
        Usage: send2peer ip [options]

        Displays the local and/or public IP address of this machine.
        Useful for identifying how other peers can connect to you.

        Options:
      HELP

      def execute(args)
        options = {
          local: false,
          public: false
        }

        parser = OptionParser.new do |opts|
          opts.banner = HELP_BANNER
          opts.on("--local", "Show only the local IP") { options[:local] = true }
          opts.on("--public", "Show only the public IP") { options[:public] = true }
        end
        parser.parse!(args)

        show_local = options[:local] || (!options[:local] && !options[:public])
        show_public = options[:public] || (!options[:local] && !options[:public])

        puts "📡 Local IP:  #{local_ip}" if show_local

        if show_public
          ip = public_ip
          if ip
            puts "🌍 Public IP: #{ip}"
          else
            puts "❌ Public IP: unavailable"
          end
        end
      end

      private

      def local_ip
        UDPSocket.open do |s|
          s.connect('8.8.8.8', 1)
          s.addr.last
        end
      rescue
        "127.0.0.1"
      end

      def public_ip
        services = [
          "https://api.ipify.org",
          "https://ifconfig.me/ip",
          "https://icanhazip.com"
        ]

        services.each do |service_url|
          begin
            uri = URI.parse(service_url)
            response = Net::HTTP.get(uri).strip
            return response unless response.empty?
          rescue StandardError
            next
          end
        end

        nil
      end
    end
  end
end
