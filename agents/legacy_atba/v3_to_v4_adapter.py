"""An adapter to run bots written for RLBot v3 in RLBot v4.

Usage:
  v3_to_v4_adapter.py --agent_module="my_legacy_agent.py"
  v3_to_v4_adapter.py (-h | --help)

Options:
  -h --help     Show this screen.
"""


from concurrent import futures
import time
import math
import grpc
from docopt import docopt
import sys

# Import the RPC protocol buffers. (needs a little bit of path hacking)
# TODO: Move RlBotFramework to a different package?
#       That way future agents don't depend on the RLBot repo.
import os
from os.path import realpath, dirname
rlbot_directory = dirname(dirname(dirname(realpath(__file__))))
# 'C:\Users\dom\Documents\GitHub\RLBot\rlbot.cfg'
sys.path.append(rlbot_directory)
from RlBotFramework.grpcsupport.protobuf import game_data_pb2
from RlBotFramework.grpcsupport.protobuf import game_data_pb2_grpc
from RlBotFramework.utils.agent_creator import import_agent




class Version3To4AdapterServer(game_data_pb2_grpc.BotServicer):

    def __init__(self, agent):
        self.agent = agent
        super().__init__()

    def GetControllerState(self, request, context):
        output_vector = None
        try:
            self.agent.get_output_vector(self.convert_request_to_game_input_packet(request))
        except Exception as e:
            print('Exception running bot: ' + str(e))
            pass
        sys.stdout.flush()
        sys.strerr.flush()
        return convert_output_vector_to_controller_state_proto

    def convert_request_to_game_input_packet(self, request):
        # TODO: inverse of proto_converter.py
        return PlayerConfiguration()

    def convert_output_vector_to_controller_state_proto(self, output_vector):
        # TODO: inverse of proto_converter.py
        return game_data_pb2.ControllerState()

def run_adapter_server(agent_module, address='localhost', port=34865):
    # Path hacking for the module to import dependencies
    sys.path.append(os.path.dirname(os.path.realpath(agent_module)))
    agent = import_agent(agent_module)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    game_data_pb2_grpc.add_BotServicer_to_server(Version3To4AdapterServer(agent), server)
    address_port = '{}:{}'.format(address, port)
    server.add_insecure_port(address_port)
    server.start()
    print('Grpc server listening on {}!'.format(address_port))
    try:
        while True:
            time.sleep(60 * 60 * 24) # one day
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    arguments = docopt(__doc__)
    # TODO: pipe in address/port too
    # print(arguments)
    run_adapter_server(arguments['--agent_module'])
