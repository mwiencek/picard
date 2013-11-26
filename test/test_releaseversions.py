import unittest
import picard
from picard import config
from picard.metadata import Metadata
from picard.mbxml import track_to_metadata, release_to_metadata
from picard.releasegroup import ReleaseGroup

settings = {
    "standardize_tracks": False,
    "standardize_artists": False,
    "standardize_releases": False,
    "translate_artist_names": False
}


class XmlNode(object):

    def __init__(self, text=u'', children={}, attribs={}):
        self.text = text
        self.children = children
        self.attribs = attribs

    def __repr__(self):
        return repr(self.__dict__)

    def __getattr__(self, name):
        try:
            return self.children[name]
        except KeyError:
            try:
                return self.attribs[name]
            except KeyError:
                raise
                #raise AttributeError, name


class ReleaseTest(unittest.TestCase):

    def test_1(self):
        config.setting = settings
        rlist = XmlNode(children={
            'metadata': [XmlNode(children={
                'release_list': [XmlNode(attribs={'count': '3'}, children={
                    'release': [
                        XmlNode(attribs={'id': '123'}, children={
                            'title': [XmlNode(text='Foo')],
                            'status': [XmlNode(text='Official')],
                            'packaging': [XmlNode(text='Jewel Case')],
                            'disambiguation': [XmlNode(text='special')],
                            'text_representation': [XmlNode(children={
                                'language': [XmlNode(text='eng')],
                                'script': [XmlNode(text='Latn')]
                                })],
                            'date': [XmlNode(text='2009-08-07')],
                            'country': [XmlNode(text='GB')],
                            'barcode': [XmlNode(text='012345678929')],
                            'medium_list': [XmlNode(attribs={'count': '1'}, children={
                                'medium': [XmlNode(children={
                                    'position': [XmlNode(text='1')],
                                    'format': [XmlNode(text='CD')],
                                    'track_list': [XmlNode(attribs={'count': '5'})],
                                })]
                            })],
                            'label_info_list': [XmlNode(attribs={'count': '1'}, children={
                                'label_info': [XmlNode(children={
                                    'catalog_number': [XmlNode(text='cat 123')],
                                    'label': [XmlNode(children={
                                        'name': [XmlNode(text='label A')]
                                    })]
                                })]
                            })]
                        }),
                        XmlNode(attribs={'id': '456'}, children={
                            'title': [XmlNode(text='Foo')],
                            'status': [XmlNode(text='Official')],
                            'packaging': [XmlNode(text='Digipak')],
                            'disambiguation': [XmlNode(text='special')],
                            'text_representation': [XmlNode(children={
                                'language': [XmlNode(text='eng')],
                                'script': [XmlNode(text='Latn')]
                                })],
                            'date': [XmlNode(text='2009-08-07')],
                            'country': [XmlNode(text='GB')],
                            'barcode': [XmlNode(text='012345678929')],
                            'medium_list': [XmlNode(attribs={'count': '1'}, children={
                                'medium': [XmlNode(children={
                                    'position': [XmlNode(text='1')],
                                    'format': [XmlNode(text='CD')],
                                    'track_list': [XmlNode(attribs={'count': '5'})],
                                })]
                            })],
                            'label_info_list': [XmlNode(attribs={'count': '1'}, children={
                                'label_info': [XmlNode(children={
                                    'catalog_number': [XmlNode(text='cat 123')],
                                    'label': [XmlNode(children={
                                        'name': [XmlNode(text='label A')]
                                    })]
                                })]
                            })]
                        }),
                        XmlNode(attribs={'id': '789'}, children={
                            'title': [XmlNode(text='Foo')],
                            'status': [XmlNode(text='Official')],
                            'packaging': [XmlNode(text='Digipak')],
                            'disambiguation': [XmlNode(text='specialx')],
                            'text_representation': [XmlNode(children={
                                'language': [XmlNode(text='eng')],
                                'script': [XmlNode(text='Latn')]
                                })],
                            'date': [XmlNode(text='2009-08-07')],
                            'country': [XmlNode(text='GB')],
                            'barcode': [XmlNode(text='012345678929')],
                            'medium_list': [XmlNode(attribs={'count': '1'}, children={
                                'medium': [XmlNode(children={
                                    'position': [XmlNode(text='1')],
                                    'format': [XmlNode(text='CD')],
                                    'track_list': [XmlNode(attribs={'count': '5'})],
                                })]
                            })],
                            'label_info_list': [XmlNode(attribs={'count': '1'}, children={
                                'label_info': [XmlNode(children={
                                    'catalog_number': [XmlNode(text='cat 123')],
                                    'label': [XmlNode(children={
                                        'name': [XmlNode(text='label A')]
                                    })]
                                })]
                            })]
                        }),
                        ]
                })]
            })]
        })
        r = ReleaseGroup(1)
        r._other_versions(rlist)
        self.assertEqual(r.versions[0]['name'],
                         '2009-08-07 / GB / label A / cat 123 / 5 / CD / Jewel Case / special')
        self.assertEqual(r.versions[1]['name'],
                         '2009-08-07 / GB / label A / cat 123 / 5 / CD / Digipak / special')
        self.assertEqual(r.versions[2]['name'],
                         '2009-08-07 / GB / label A / cat 123 / 5 / CD / Digipak / specialx')

    def test_2(self):
        config.setting = settings
        rlist = XmlNode(children={
            'metadata': [XmlNode(children={
                'release_list': [XmlNode(attribs={'count': '2'}, children={
                    'release': [
                        XmlNode(attribs={'id': '789'}, children={
                            'title': [XmlNode(text='Foox')],
                            'status': [XmlNode(text='Official')],
                            'disambiguation': [XmlNode(text='special A')],
                            'text_representation': [XmlNode(children={
                                'language': [XmlNode(text='eng')],
                                'script': [XmlNode(text='Latn')]
                                })],
                            'date': [XmlNode(text='2011-08-07')],
                            'country': [XmlNode(text='FR')],
                            'medium_list': [XmlNode(attribs={'count': '1'}, children={
                                'medium': [XmlNode(children={
                                    'position': [XmlNode(text='1')],
                                    'format': [XmlNode(text='CD')],
                                    'track_list': [XmlNode(attribs={'count': '5'})],
                                })]
                            })],
                            'label_info_list': [XmlNode(attribs={'count': '1'}, children={
                                'label_info': [XmlNode(children={
                                    'catalog_number': [XmlNode(text='cat 123')],
                                    'label': [XmlNode(children={
                                        'name': [XmlNode(text='label A')]
                                    })]
                                })]
                            })]
                        }),
                        XmlNode(attribs={'id': '789'}, children={
                            'title': [XmlNode(text='Foox')],
                            'status': [XmlNode(text='Official')],
                            'text_representation': [XmlNode(children={
                                'language': [XmlNode(text='eng')],
                                'script': [XmlNode(text='Latn')]
                                })],
                            'date': [XmlNode(text='2011-08-07')],
                            'country': [XmlNode(text='FR')],
                            'medium_list': [XmlNode(attribs={'count': '1'}, children={
                                'medium': [XmlNode(children={
                                    'position': [XmlNode(text='1')],
                                    'format': [XmlNode(text='CD')],
                                    'track_list': [XmlNode(attribs={'count': '5'})],
                                })]
                            })],
                            'label_info_list': [XmlNode(attribs={'count': '1'}, children={
                                'label_info': [XmlNode(children={
                                    'catalog_number': [XmlNode(text='cat 123')],
                                    'label': [XmlNode(children={
                                        'name': [XmlNode(text='label A')]
                                    })]
                                })]
                            })]
                        }),
                        ]
                })]
            })]
        })
        r = ReleaseGroup(1)
        r._other_versions(rlist)
        self.assertEqual(r.versions[0]['name'],
                         '2011-08-07 / FR / label A / cat 123 / 5 / CD / special A')
        self.assertEqual(r.versions[1]['name'],
                         '2011-08-07 / FR / label A / cat 123 / 5 / CD')

    def test_3(self):
        config.setting = settings
        rlist = XmlNode(children={
            'metadata': [XmlNode(children={
                'release_list': [XmlNode(attribs={'count': '2'}, children={
                    'release': [
                        XmlNode(attribs={'id': '789'}, children={
                            'title': [XmlNode(text='Foox')],
                            'status': [XmlNode(text='Official')],
                            'packaging': [XmlNode(text='Digipak')],
                            'disambiguation': [XmlNode(text='specialx')],
                            'text_representation': [XmlNode(children={
                                'language': [XmlNode(text='eng')],
                                'script': [XmlNode(text='Latn')]
                                })],
                            'date': [XmlNode(text='2009-08-07')],
                            'country': [XmlNode(text='FR')],
                            'barcode': [XmlNode(text='012345678929')],
                            'medium_list': [XmlNode(attribs={'count': '1'}, children={
                                'medium': [XmlNode(children={
                                    'position': [XmlNode(text='1')],
                                    'format': [XmlNode(text='CD')],
                                    'track_list': [XmlNode(attribs={'count': '5'})],
                                })]
                            })],
                            'label_info_list': [XmlNode(attribs={'count': '1'}, children={
                                'label_info': [XmlNode(children={
                                    'catalog_number': [XmlNode(text='cat 123')],
                                    'label': [XmlNode(children={
                                        'name': [XmlNode(text='label A')]
                                    })]
                                })]
                            })]
                        }),
                        XmlNode(attribs={'id': '789'}, children={
                            'title': [XmlNode(text='Foox')],
                            'status': [XmlNode(text='Official')],
                            'packaging': [XmlNode(text='Digipak')],
                            'disambiguation': [XmlNode(text='specialx')],
                            'text_representation': [XmlNode(children={
                                'language': [XmlNode(text='eng')],
                                'script': [XmlNode(text='Latn')]
                                })],
                            'date': [XmlNode(text='2009-08-07')],
                            'country': [XmlNode(text='FR')],
                            'barcode': [XmlNode(text='')],
                            'medium_list': [XmlNode(attribs={'count': '1'}, children={
                                'medium': [XmlNode(children={
                                    'position': [XmlNode(text='1')],
                                    'format': [XmlNode(text='CD')],
                                    'track_list': [XmlNode(attribs={'count': '5'})],
                                })]
                            })],
                            'label_info_list': [XmlNode(attribs={'count': '1'}, children={
                                'label_info': [XmlNode(children={
                                    'catalog_number': [XmlNode(text='cat 123')],
                                    'label': [XmlNode(children={
                                        'name': [XmlNode(text='label A')]
                                    })]
                                })]
                            })]
                        }),
                        ]
                })]
            })]
        })
        r = ReleaseGroup(1)
        r._other_versions(rlist)
        self.assertEqual(r.versions[0]['name'],
                         '2009-08-07 / FR / label A / cat 123 / 5 / CD / 012345678929')
        self.assertEqual(r.versions[1]['name'],
                         '2009-08-07 / FR / label A / cat 123 / 5 / CD / [none]')
