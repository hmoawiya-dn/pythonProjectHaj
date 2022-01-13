


#
# This class wraps around an integer value and represents a value in binary representation.
# This is used to simlify output.
#
class _Bits(object):

	__slots__ = (
		"value",
	)

	def __init__(self, value:int):
		assert isinstance(value, int)
		assert value >= 0
		self.value = value
	#

	def __repr__(self):
		s = bin(self.value)[2:]
		n = len(s)
		if (n == 8) or (n == 16) or (n == 32) or (n == 64):
			return "b" + s
		elif n < 8:
			r = n % 8
			return "b" + ("0" * (8 - r)) + s
		elif n < 16:
			r = n % 16
			return "b" + ("0" * (16 - r)) + s
		elif n < 32:
			r = n % 32
			return "b" + ("0" * (32 - r)) + s
		elif n < 64:
			r = n % 64
			return "b" + ("0" * (64 - r)) + s
		else:
			r = n % 8
			return "b" + ("0" * (8 - r)) + s
	#

	def __str__(self):
		return self.__repr__()
	#

#






