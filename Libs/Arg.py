from argparse import ArgumentParser

def get_option(batch, epoch):
    argparser = ArgumentParser()
    #argparser.add_argument('-o', '--offline', type = int, default=batch, help = 'Specify size of batch')
    argparser.add_argument('-db', '--database', type = char, default=batch, help = 'Specify size of batch', action="gogogo")
    #argparser.add_argument('-c', '--batch', type = int, default=batch, help = 'Specify size of batch')

    return argparser.parse_args()


#args=get_option(BATCH_SIZE, EPOCHS)
parser = ArgumentParser()
parser.add_argument('-db', '--database', type = str, default="zoo.db", help = 'Specify size of batch')
parser.add_argument('--offline', type = bool, default=False, help = 'Specify size of batch')
args = parser.parse_args()
print(args)
