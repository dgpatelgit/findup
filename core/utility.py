
class Utility:
  # Replace all single quote ' in string with this string.
  SUBSTITUTE_SINGLE_QUOTE = "_@$1Q$@_"

  # Replace all double quote " in string with this string.
  SUBSTITUTE_DOUBLE_QUOTE = "_@$2Q$@_"

  def encodeDBString(self, inStr):
    return inStr.replace("'", self.SUBSTITUTE_SINGLE_QUOTE).replace('"', self.SUBSTITUTE_DOUBLE_QUOTE)

  def decodeDBString(self, inStr):
    return inStr.replace(self.SUBSTITUTE_SINGLE_QUOTE, "'").replace(self.SUBSTITUTE_DOUBLE_QUOTE, '"')
