from random import shuffle

import soco
from soco import SoCo
from soco.plugins.sharelink import ShareLinkPlugin

speaker: SoCo = soco.discovery.by_name("LivingRoom")
sharelink = ShareLinkPlugin(speaker)

sharelink.add_share_link_to_queue("spotify:playlist:3PhrgXmaPgAqKuYCNP8QrH")

queue = speaker.get_queue()
speaker.clear_queue()
shuffled_queue = list(queue)
shuffle(shuffled_queue)
speaker.add_multiple_to_queue(shuffled_queue)


# speaker.play()
speaker.play_from_queue(0, start=True)
# speaker.next()
# speaker.stop()
