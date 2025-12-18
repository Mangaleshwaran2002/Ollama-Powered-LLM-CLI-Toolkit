from ollama import chat 

def add(a: int, b: int) -> int:
  """Add two numbers"""
  """
  Args:
    a: The first number
    b: The second number

  Returns:
    The sum of the two numbers
  """
  return a + b


def multiply(a: int, b: int) -> int:
  """Multiply two numbers"""
  """
  Args:
    a: The first number
    b: The second number

  Returns:
    The product of the two numbers
  """
  return a * b


available_functions = {
  'add': add,
  'multiply': multiply,
}


messages = [{'role': 'user', 'content': "What is (4+11)*12?"}]

while True:
  stream = chat(
    model='qwen3:4b',
    messages=messages,
    tools=[add, multiply],
    stream=True,
    think=True,
  )

  thinking = ''
  content = ''
  tool_calls = []

  done_thinking = False
  # accumulate the partial fields
  for chunk in stream:
    if chunk.message.thinking:
      thinking += chunk.message.thinking
      print(chunk.message.thinking, end='', flush=True)
    if chunk.message.content:
      if not done_thinking:
        done_thinking = True
        print('\n')
      content += chunk.message.content
      print(chunk.message.content, end='', flush=True)
    if chunk.message.tool_calls:
      tool_calls.extend(chunk.message.tool_calls)
      print(chunk.message.tool_calls)
  print("\n\nthinking: \n",thinking)
  print("\n\ncontent: \n",content)
  break
  # append accumulated fields to the messages
  # if thinking or content or tool_calls:
  #   messages.append({'role': 'assistant', 'thinking': thinking, 'content': content, 'tool_calls': tool_calls})

  # if not tool_calls:
  #   break
