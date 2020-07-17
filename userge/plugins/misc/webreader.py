"""
Scrape the article, translate and push to telegraph
"""
import re

from newspaper import Article, ArticleException
from telegraph import Telegraph
from googletrans import Translator

from userge import userge, Message


@userge.on_cmd("wr", about={
	'header': "Web Reader",
	'usage': "{tr}wr [url] [*language]"})
async def webreader(message: Message):
	regex: str = r'(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.' \
		r'[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*))'

	tgr = Telegraph()
	tl = Translator()
	inp = message.input_str

	if len(inp.split()) > 1:
		lang = inp.split()[1]
	else: lang = None

	url: str = inp.split()[0]
	url: str = re.search(regex, url).group(1)

	article: Article = Article(url)

	try:
		await message.edit("Getting text ...")
		article.download()
		article.parse()
		text = f"{article.text}"
	except ArticleException:
		return await message.edit("Failed to scrape the article!")

	if lang:
		try:
			await message.edit("Translating Text to `{}` ...".format(lang))
			text = tl.translate(text, dest=lang, src="auto")
			text = text.text
			return await message.edit(text[:4096])
		except ValueError as err:
			return await message.edit("Error: `{}`".format(str(err)))

	await message.edit("Uploading to telegraph ...")
	tgr.create_account(short_name='13378')
	response = tgr.create_page(
		f"{article.title}",
		html_content="<p>{}</p>".format(text.replace("\n", "<br>"))
	)

	await message.edit(
		"[Click Here](https://telegra.ph/{})".format(
			response["path"]
		)
	)


