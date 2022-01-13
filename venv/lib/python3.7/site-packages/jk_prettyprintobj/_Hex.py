


#
# This class wraps around an integer value and represents a hex value.
# This is used to simlify output.
#
class _Hex(object):

	__slots__ = (
		"value",
	)

	def __init__(self, value:int):
		assert isinstance(value, int)
		assert value >= 0
		self.value = value
	#

	def __repr__(self):
		s = hex(self.value)[2:]
		n = len(s)
		if n == 1:
			return "x0" + s
		elif n == 2:
			return "x" + s
		else:
			r = n % 4
			return "x" + ("0" * (4 - r)) + s
	#

	def __str__(self):
		return self.__repr__()
	#

#






