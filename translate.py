from pydub import AudioSegment 
csv='./dataset/dataset.csv'
handle = open(csv, 'r')
rawlines = handle.read().split('\n')
handle.close()
datalist = [line.split(',') for line in rawlines]

#for url, target_emotion in datalist:
sound  = AudioSegment.from_wav('./dataset/tess/OA_bite_neutral.wav')
sound = sound.set_channels(1)
sound.export("./dataset/tess/angry/OA_bite_neutral.wav")

