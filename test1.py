import logging

FORMAT = '%(asctime)-15s\tThread info: %(thread)d %(threadName)s %(message)s'
logging.basicConfig(format=FORMAT)

logging.info('I am {}'.format(20))
logging.warning('I am {}'.format(20))skdfjskkjlfds