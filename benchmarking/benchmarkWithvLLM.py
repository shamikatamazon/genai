import requests
import json
import random
#from prometheus_client import start_http_server, Summary
from prometheus_client import start_http_server, multiprocess, CollectorRegistry, Summary, Counter
from multiprocessing import Process
import shutil
import time, os

url = 'http://ec2-3-88-200-227.compute-1.amazonaws.com:8000/v1/completions'

# ensure variable exists, and ensure defined folder is clean on start
prome_stats = os.environ["PROMETHEUS_MULTIPROC_DIR"]
if os.path.exists(prome_stats):
    shutil.rmtree(prome_stats)
os.mkdir(prome_stats)


listOfPrompts = [
"Answer as true or false only and do not provide any explanation, is Mt. Everest the tallest mountain in the world ?",
"Write a poem about nature.",
"Explain quantum computing in simple terms. ",
"How would you describe yourself in one sentence?",
"Write a shopping list for a dinner party.",
"Give advice for someone learning to play guitar.",
"Translate this sentence into Spanish: My name is John and I live in London.",
"Summarize the plot of the Harry Potter book series in one paragraph.",
"Define photosynthesis in a few sentences.",
"Describe the taste of an orange.",
"Write a haiku poem about the ocean.",
"Explain baseball rules to someone who has never seen a game.",
"Describe a typical morning routine.",
"Give 5 tips for healthy eating habits.  ",
"Write a short children's story involving animals.",
"Explain how to change a car tire step-by-step.",
"List 10 random objects you'd find in a desk drawer.",
"Provide directions from my house to the grocery store 3 blocks away.  ",
"Describe the plot of your favorite movie.",
"Write a fan letter to your favorite celebrity.",
"Explain how to make a simple pasta dish.",
"Describe the difference between cats and dogs.",
"Give advice to someone learning how to drive.",
"Write a short fairytale with a princess and dragon. ",
"Explain the causes of climate change.",
"Describe 5 landmarks in Paris, France.",
"Write a list of gift ideas for a 10 year old girl.",
"Explain the rules of football for non-fans.",
"Describe 3 memorable vacations you've taken.",
"Write a motivational quote about perseverance. ",
"Give tips for throwing a surprise party.",
"Explain how smartphones have impacted society.",
"Describe your dream house.",
"Write a short review of your favorite movie, book or album.",
"Explain the difference between type 1 and type 2 diabetes.  ",
"List pros and cons of living in a big city versus small town.",
"Write a short story about finding treasure on a beach.",
"Describe the perfect pizza.",
"Explain how planes are able to fly.",
"Write a letter to your future self 20 years from now.",
"Describe how you take your coffee or tea.",
"Explain 5 causes of the Great Depression.",
"Describe the appearance of a close friend or family member.",
"Provide tips for a first-time homebuyer. ",
"Write about your favorite hobby and how you got started.",
"Explain the role of DNA and genes in biology.",
"Describe the plot of a book you've read recently.  ",
"Write about an inspirational figure you admire. ",
"Explain how to fold paper into an origami crane.",
"Describe the experience of walking through a forest.",
"Explain what makes a good friendship.",
"Write about an amusing childhood memory.",
"Describe your ideal vacation spot.",
"Explain how the internet functions.",
"List 3 goals you have for the next 5 years.",
"Write about a time you learned a difficult lesson.",
"Explain basic rules of grammar and punctuation. ",
"Describe your favorite meal or food.",
"Give advice for someone feeling depressed or anxious.",
"Write about a current news event that interests you.",
"Explain how a vaccine works.",
"List 5 items you would bring if stranded on a deserted island.  ",
"Describe your dream job or career.",
"Write a short biography of yourself.",
"Explain how solar eclipses occur.",
"Describe a place you've always wanted to visit.  ",
"Explain the difference between winter and summer.",
"Write about an inspiring public figure you admire.",
"Describe the experience of riding a rollercoaster. ",
"Explain the pros and cons of social media.",
"Describe a memorable day from your childhood.",
"Explain how to grow vegetables in a garden.",
"Write a fan letter to your favorite author.",
"Explain the plot of a Shakespeare play in simple terms.",
"Describe what you see when looking out your window.",
"List 5 personal goals you have achieved.",
"Write a short fairytale involving magical creatures.",
"Explain how electricity is generated.",
"Describe your favorite place in nature. ",
"Write about a book that had a profound impact on you.",
"Explain how weather forecasting and predictions work.",
"List 10 random items you'd find in a backpack.",
"Describe the experience of walking in heavy rain.",
"Write about an impactful teacher you had in school.",
"Explain photosynthesis in simple terms.",
"Describe your favorite celebrity or musician.",
"Write about an amusing experience that made you laugh.  ",
"Explain how to ride a bike to someone unfamiliar.",
"Describe the plot of your favorite book.",
"Explain how WiFi internet connections work.",
"Write about your favorite place to travel.",
"Describe the experience of seeing a lunar eclipse.  ",
"Explain how search engines like Google work.",
"List 5 fun indoor activities for kids.",
"Describe your favorite season and why you like it. ",
"Explain how to play a simple card game.",
"Write a short poem about friendship.",
"Describe how smartphones have changed daily life.",
"Explain baking basics to a beginner.",
"Write about an impactful experience that changed your life.",
"Describe your vision for your life in 10 years.",
"Write a rap song about vegetables",
  "Come up with new flavored jelly beans like rotten egg and earthworm",
  "Describe how an alien would react at their first football game", 
  "Explain quantum physics using only food references",
  "Write a bake sale flyer for vampires",
  "Invent a knock-knock joke with 'Boo' as the punchline",
  "Describe a day in the life of a stuffed animal",
  "Give advice to a superhero about how to fight crime and balance work life",
  "Write a monologue as the grape that fell off the fruit stand", 
  "Describe the most ridiculous looking mythical creature you can imagine",
  "Pitch a reality TV show about competitive cheese rolling",
  "Retell Romeo and Juliet from the perspective of Juliet's pony",
  "Write a children's book about a dog astronaut",
  "Describe the most unusual ice cream flavors invented",
  "Compose a song about getting your wisdom teeth removed", 
  "Write a resignation letter for Santa Claus quitting the North Pole",
  "Imagine a world where shoes eat socks instead of people wearing socks",
  "Explain how you would prank call the Greek Gods of Mount Olympus",
  "Describe what animals do in elevators when humans aren't around",
  "Write about your experience taste testing the world's spiciest peppers",
  "Pitch a movie crossover between Star Wars and Spongebob Squarepants", 
  "Describe what Santa Claus does in the offseason after Christmas",
  "Write about running a hotel for dogs and what services it would offer",
  "Describe the experience of a slice of pizza going through the human digestive system",
  "Compose a song from the perspective of a stray sock missing its pair",
  "Explain how you'd survive a sharknado if one hit your city",
  "Write a breaking news alert about pandas who have learned Kung Fu and rebelled against zookeepers",
  "Describe what various desserts would talk about if they could speak to each other",
  "Explain dog training techniques for teaching dogs to become ninjas",
  "Describe a day in the life of the world's most introverted cat",
  "Pitch a sitcom about unicorns trying to make it in the big city",
  "Write an acceptance speech for an Academy Award won by a banana",
  "Compose a song about the existential dread of having an ancient curse put upon you by a mummy",
  "Retell the plot of Jaws from the perspective of the shark",
  "Describe a mad scientist's invention for a machine that gives you terrible hair days on command",
  "Explain what the world would be like if dogs ruled over humans as masters",
  "Write about your experience of fighting a professional boxer while your hands were replaced with lasagna noodles",
  "Describe bizarre Olympic events that you'd like to see added to future games",
  "Compose a rap song from the perspective of a slice of pizza",
  "Pitch a reality competition show starring different flavors of ice cream",
  "Write about being the first caveman to discover fire and what you imagined its magic powers were",
  "Describe what kind of mischief and hijinks a group of raccoons would get up to in a grocery store at night if humans weren't around",
  "Invent a mythical creature that is half unicorn, half dinosaur",
  "Explain what it would be like to climb Mount Everest if the mountain was made of pudding",
  "Write about your experience tasting the world's spiciest chili pepper and breathing fire afterward",
  "Describe the experience of a marshmallow fighting a smore in an epic battle",
  "Compose a song from the perspective of a weary time traveler just trying to get some sleep while the timeline keeps shifting around them",
  "Pitch a sitcom about cavemen living modern lives and struggling with technology"
]

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
PROMPT_TOKEN_COUNTER = Counter('prompt_token_counter', 'tokens in prompt')
GENERATED_TOKEN_COUNTER = Counter('generated_token_counter', 'tokens generated by LLM')
REQUESTS_COUNTER = Counter('enduser_requests_counter', 'tokens generated by LLM')



def make_request_to_llm():
  
    while True:
      
      random_num = random.randint(0,len(listOfPrompts)-1) 
      
      random_num_beam_search = 1
      
      prompt = "[INST]" + listOfPrompts[random_num] + "[/INST]"
      
      
      # Sample data to send as JSON
      data = {
      	"model" : "mistralai/Mistral-7B-Instruct-v0.1",
      	"prompt" : prompt,
      	"max_tokens" : 1000,
      	"n" : random_num_beam_search,
      	"temperature" : 0.5,
      	"top_p" : 0.6
      }
      
      start = time.time()
      
      # Make POST request and send JSON data
      response = requests.post(url, json=data)
      REQUESTS_COUNTER.inc()
      
      end = time.time()
      
      if response.status_code == 200:
        responseJson = json.loads(response.text)
        
        promptTokens =  responseJson["usage"]["prompt_tokens"]
        generatedTokens =  responseJson["usage"]["completion_tokens"]
      
        REQUEST_TIME.observe((end-start))
        PROMPT_TOKEN_COUNTER.inc(promptTokens)
        GENERATED_TOKEN_COUNTER.inc(generatedTokens)
        
        
      else:
        print('Request Failed') 

if __name__ == '__main__':
    
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    start_http_server(9000, registry=registry)
    
    for i in range(1,21):
      p = Process(target=make_request_to_llm, args=())
      a = p.start()