class Federation:
    static_id = 0
    MAX_SIZE = 4

    def __init__(self, fed_creator):
        self.id = Federation.static_id
        Federation.static_id += 1
        self.members = [fed_creator]
        fed_creator.federation = self

    def needed_resources(self):
        res = 0
        for m in self.members:
            res += m.all_resources - m.required_resources
        return res

    def add_member(self, provider):
        if provider in self.members:
            raise Exception(str(provider) + " already exists in Federation " + str(self.id))
        self.members.append(provider)
        provider.federation = self

    def remove_member(self, provider):
        if provider not in self.members:
            raise Exception(str(provider) + " does not exist in Federation " + str(self.id))
        self.members.remove(provider)
        # if self.get_member_size() == 0:
        #     del self

    def get_member_size(self):
        return len(self.members)

    def __str__(self):
        return "Federation " + str(self.id) + " contains " + str(self.members)

    def __repr__(self):
        return str(self)
