# This is the creation of the class Seq and its methods - Practice 1

# Create class Seq
class Seq:
    """A class for representing sequences."""

    def __init__(self, strbases):  # Initialize the sequence with the value passed as argument when creating the object
        self.strbases = strbases

    def len(self):  # Return the length of the strings of bases
        return len(self.strbases)

    def complement(self):  # Returns the complementary string of Dna of the sequence given
        co_bases = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
        co_string = self.strbases.maketrans(co_bases)
        complementary_b = self.strbases.translate(co_string)
        return Seq(complementary_b)

    def reverse(self):  # Returns a new sequence, that is the reverse of the sequence given
        rev_bases = self.strbases[::-1]
        return Seq(rev_bases)

    def count(self, base):  # Returns the number of bases 'base' that appear in the sequence given
        nb = self.strbases.count(base)
        return nb

    def perc(self, base):  # Returns the percentage of the base 'base' over the total
        tl = len(self.strbases)
        if tl > 0:
            nb = self.count(base)
            perc = round(100.0 * nb / tl, 1)
        else:
            perc = 0
        return perc
