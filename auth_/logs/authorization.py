import logging
logger = logging.getLogger('authorization')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(filename='authorization.log', mode='a')
file_formatter = logging.Formatter('%(asctime)s -- %(levelname)s: -- %(message)s')
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.WARNING)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(name)s -- %(levelname)s -- %(message)s')
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.DEBUG)


logger.addHandler(file_handler)
logger.addHandler(console_handler)
