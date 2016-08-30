$GO = <<SCRIPT
  sudo add-apt-repository ppa:ubuntu-lxc/lxd-stable -y
  sudo apt-get update && sudo apt-get install golang python-pip -y
SCRIPT

boxes = [
  {
    :name => "random",
    :mem  => "2048",
    :cpu  => "2",
    :ip   => "192.168.56.188"
  },
]

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  boxes.each do |opts|
    config.vm.define opts[:name] do |config|
      config.vm.hostname = opts[:name]
      config.vm.network 'private_network', ip: opts[:ip]

      config.vm.provider "virtualbox" do |v|
        v.customize ["modifyvm", :id, "--memory", opts[:mem]]
        v.customize ["modifyvm", :id, "--cpus", opts[:cpu]]
      end
      config.vm.provision "shell", inline: $GO
    end
  end
end
