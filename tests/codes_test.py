import os
from codes import main

def test_codes():
    path = os.path.join(os.path.dirname(__file__), "resources", "songs.pickle")
    # Ensure 3,4,5,6,7 length codes can be generated
    for i in range(3,8):
        main(path, i)
