class Encoder : 
    def __init__(self, vocabsize=10000):
        self.vocabsize=vocabsize

    def encoder(self , text):
        tokens = text.split() # this makes an array or word in the statement
        encodedTokens = []

        for token in tokens:
            asciiVal = "".join(
                str(ord(char)) for char in token # join the ascii of the letters eg : 10233 and falana 
            )

            encodedToken = int(asciiVal)
            encodedTokens.append(encodedToken)
        return encodedTokens
    
    def decoder(self ,encodedTokens):
        decodedTokens = []

        for number in encodedTokens:
            digits = str(number)
            i = 0 
            token = ""

            while i < len(digits): 
                if (
                    i+3 <= len(digits) and 32 <= int(digits[i : i+3]) <= 126 
                ):
                    token += chr(int(digits[i : i+3]))
                    i+=3
                elif i + 2 <= len(digits) and 32 <= int(digits[i : i+2]) <= 126:
                    token += chr(int(digits[i : i+2]))
                    i += 2
                else: 
                    token += "<UNK>"
                    break

            decodedTokens.append(token)
        return " ".join(decodedTokens)


# if (
#     __name__ == "__main__"
# ): 
#     # main()       
