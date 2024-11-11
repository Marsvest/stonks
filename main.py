from model import SimModel

text1 = 'hi i want to show you'
text2 = 'hi i want to show you'

model = SimModel()

print(model.get_similarity(text1, text2))