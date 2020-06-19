import sys
import json
import itertools
import nltk
from Levenshtein import *
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
matching_threshold = 0
import tqdm

def cluster_match(cluster1, cluster2, pcontext):
    # here we implement tokenwise match
    for c1_word in cluster1:
        for c2_word in cluster2:
            c1_text = list(zip(*c1_word))[0]
            c2_text = list(zip(*c2_word))[0]

            str1 = " ".join(c1_text).lower()
            str2 = " ".join(c2_text).lower()
            
            rtio = ratio(str1, str2)
            if(rtio>=matching_threshold):
                if(pcontext):
                    print(str2, "||", str1, rtio, matching_threshold, flush=True)
                return True
    return False



def match_merge_clusters(new_cluster, old_clusters):
    'write a function to match text'
    if(old_clusters == []):
        old_clusters.append(new_cluster)
        # print(new_cluster,'\n')
        return True
    
    for each_cluster in old_clusters:
        try:
            if(cluster_match(new_cluster, each_cluster, False)):
                each_cluster.extend(new_cluster)
                # print(each_cluster)
                return True
        except:
            import ipdb; ipdb.set_trace()
    old_clusters.append(new_cluster)
    # print(new_cluster,'\n')
    return False



def match_clusters(new_cluster, old_clusters):
    'write a function to match text'
    if(old_clusters == []):
        # old_clusters.append(new_cluster)
        return False
    
    for each_cluster in old_clusters:
        try:
            if(cluster_match(new_cluster, each_cluster, True)):
                # each_cluster.extend(new_cluster)
                return True
        except:
            import ipdb; ipdb.set_trace()
    # old_clusters.append(new_cluster)
    return False


def isPNoun(tagged_list):
    accepted_list = ['NN', 'NNS', 'NNP', 'NNPS']

    for token, tag in tagged_list:
        if(tag in accepted_list):
            return True
    return False


def analysis(part_id, part_clusters, stats_dict):
    # print(part_id, flush=True)
    # return
    # import ipdb; ipdb.set_trace()
    first_part = False
    conllId , partid = docid(part_id)
    # print(conllId, partid)
    token_list = list(itertools.chain.from_iterable(part_clusters["sentences"]))
    cluster_list = part_clusters["clusters"] # list of list of [start, end] of mentions
    # for each_cluster in cluster_list:
    #     for each_mention in each_cluster:``
    #         try:
    #             each_mention.append[str(partid)]
    #         except:
    #             import ipdb; ipdb.set_trace()

    if(conllId not in stats_dict):
        stats_dict[conllId] = {"clusters":[], "cluster_count":0, "commonnoun_cluster_count":0, "propernoun_cluster_count":0, \
            "matching_clusters":0, "doc_count":1, "token_count":len(token_list), "first_part_clusters":len(cluster_list)}
        first_part = True
    else:
        stats_dict[conllId]["doc_count"]+=1
        stats_dict[conllId]["token_count"]+=len(token_list)

    cluster_text_list = []
    for each_cluster in cluster_list:
        cluster_text = []
        for men in each_cluster:
            men_tokens = token_list[men[0]:men[1]+1]
            men_tagged_tokens = nltk.pos_tag(men_tokens)
            if(isPNoun(men_tagged_tokens)):
                cluster_text.append(men_tagged_tokens)
        cluster_text_list.append(cluster_text)



    # print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||", flush=True)
    # counting merges  
    for cluster_text in cluster_text_list:
        if(len(cluster_text)>0):
            stats_dict[conllId]["propernoun_cluster_count"]+=1
            if(match_clusters(cluster_text, stats_dict[conllId]["clusters"])):
                stats_dict[conllId]["matching_clusters"]+=1
        else:
            stats_dict[conllId]["commonnoun_cluster_count"]+=1
            # stats_dict[conllId]["clusters"].append(cluster_text)

        stats_dict[conllId]["cluster_count"]+=1

    # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++", flush=True)


    # merging clusters  
    for cluster_text in cluster_text_list:
        if(len(cluster_text)>0):
            match_merge_clusters(cluster_text, stats_dict[conllId]["clusters"])        
        else:
            stats_dict[conllId]["clusters"].append(cluster_text)

    if(first_part):
        assert stats_dict[conllId]["matching_clusters"]==0

def docid(file_name):
    try:
        doc, part = file_name.rsplit('_', 1)
    except:
        import ipdb; ipdb.set_trace()
    return doc, part





def doc_size_analysis():
    in_fn = sys.argv[1]
    doc_len = []
    stats_dict = {}
    breaker = 0;
    with open(in_fn, 'r') as f:
        for line in f:
            # print(line)
            # if(breaker>9):
            #     break
            # breaker+=1

            data = json.loads(line)
            # import ipdb; ipdb.set_trace()

            # doc_list.append(docid(data["doc_key"])[0])
            # do stuff
            token_list = list(itertools.chain.from_iterable(data["sentences"]))
            doc_len.append(len(token_list))
            # analysis(data["doc_key"], data, stats_dict)
        print("Total size of documents", len(doc_len))
        print("Mean len of documents", np.mean(doc_len))
        print("Std of documents", np.std(doc_len))

        hist = np.histogram(doc_len, bins=np.arange(20)*500)
        print(hist)





def doc_len_analysis():
    # in_fn = sys.argv[1]
    # doc_list = []
    # stats_dict = {}
    # breaker = 0;
    # with open(in_fn, 'r') as f:
    #     for line in f:
    #         # print(line)
    #         # if(breaker>9):
    #         #     break
    #         # breaker+=1

    #         data = json.loads(line)
    #         # import ipdb; ipdb.set_trace()

    #         # doc_list.append(docid(data["doc_key"])[0])
    #         # do stuff
    #         analysis(data["doc_key"], data, stats_dict)

    # print("done finding files", breaker)
    # # print(stats_dict)
    # # print(stats_dict[""])
    # # print(len(stats_dict))
    # # import ipdb; ipdb.set_trace()
    with open("./Analysis_Ontonotes.json", "w") as f:
        json.dump(stats_dict, f)

    with open("./Analysis_Ontonotes.json", "r") as f:
        stats_dict = json.load(f)

    print("Total Number of Documents", len(stats_dict))

    doc_len_list = []
    for each_doc in stats_dict:
        # print(stats_dict[each_doc]["token_count"])
        doc_len_list.append(stats_dict[each_doc]["token_count"])

    print("Mean Size of Documents", np.mean(doc_len_list))
    print("Standard Deviation of Documents' size", np.std(doc_len_list))


    hist = np.histogram(doc_len_list, bins=np.arange(70)*500)
    # plt.hist(hist[0], density=True, bins=hist[1])
    # import ipdb; ipdb.set_trace()
    print(hist)




    with open("./Analysis_Ontonotes.json", "r") as f:
        stats_dict = json.load(f)


    doc_len_list = []
    for each_doc in stats_dict:
        # print(stats_dict[each_doc]["token_count"])
        doc_len_list.append(stats_dict[each_doc]["doc_count"])

    hist = np.histogram(doc_len_list, bins=np.arange(40))
    # plt.hist(hist[0], density=True, bins=hist[1])
    # import ipdb; ipdb.set_trace()
    print(hist)





def cluster_matching_analysis():
    in_fn = sys.argv[1]
    # for matching_threshold in np.linspace(0.7,0.95,6):
    global matching_threshold
    thres_wise_percent_list = []
    for matching_threshold in [0.9, 0.95]:
        doc_list = []
        stats_dict = {}
        breaker = 0;
        with open(in_fn, 'r') as f:
            for line in tqdm.tqdm(f):
                data = json.loads(line)
                # import ipdb; ipdb.set_trace()
                
                # doc_list.append(docid(data["doc_key"])[0])
                # do stuff
                analysis(data["doc_key"], data, stats_dict)
        # print(stats_dict, "\n\n\n\n\n")

        zero_count=0
        doc_percent_list = []
        doc_list = []
        for each_doc in stats_dict:
            if(stats_dict[each_doc]["cluster_count"]>0 and stats_dict[each_doc]["doc_count"] >1):
                doc_percent_list.append((stats_dict[each_doc]["matching_clusters"]*1.0/(stats_dict[each_doc]["cluster_count"]-stats_dict[each_doc]["first_part_clusters"]), each_doc))

            else:
                print(stats_dict[each_doc], "\n\n\n\n\n")
                zero_count+=1
        # import ipdb; ipdb.set_trace()
        res0 = list(zip(*doc_percent_list))[0]
        res1 = list(zip(*doc_percent_list))[1]
        thres_wise_percent_list.append(np.mean(res0))
        print(np.mean(res0))

        import ipdb; ipdb.set_trace()
        print(thres_wise_percent_list)
        # for each in stats_dict:
        with open("./Analysis_FT_Ontonotes_{}.json".format(matching_threshold), "w") as f:
            json.dump(stats_dict, f)





    # mean_matching = []
    # for matching_threshold in np.linspace(1,0.5,11):
    #     zero_count = 0
    #     doc_percent_list = []
    #     with open("./Analysis_FT_Ontonotes_{}.json".format(matching_threshold), "r") as f:
    #         stats_dict = json.load(f)
    #     for each_doc in stats_dict:
    #         if(stats_dict[each_doc]["cluster_count"]>0 and stats_dict[each_doc]["doc_count"] >1):
    #             doc_percent_list.append(stats_dict[each_doc]["matching_clusters"]*1.0/stats_dict[each_doc]["cluster_count"])
    #         else:
    #             print(stats_dict[each_doc], "\n\n\n\n\n")
    #             doc_percent_list.append(0)
    #             zero_count+=1
    #     # import ipdb; ipdb.set_trace()
    #     print(zero_count)

    #     # print(doc_percent_list)
    #     mean_matching.append(np.mean(doc_percent_list))

    # print(mean_matching)


    # mean_matching = []
    # for matching_threshold in np.linspace(1,0.5,11):
    #     match_list = []
    #     clus_list = []
    #     zero_count = 0
    #     with open("./Analysis_FT_Ontonotes_{}.json".format(matching_threshold), "r") as f:
    #         stats_dict = json.load(f)

    #     for each_doc in stats_dict:
    #         if(stats_dict[each_doc]["cluster_count"]>0 and stats_dict[each_doc]["doc_count"] >1):
    #             match_list.append(stats_dict[each_doc]["matching_clusters"])
    #             clus_list.append(stats_dict[each_doc]["propernoun_cluster_count"])
    #         else:
    #             print(stats_dict[each_doc], "\n\n\n\n\n")
    #             zero_count+=1
    #     # import ipdb; ipdb.set_trace()
    #     print(zero_count)

    #     print(np.sum(match_list)*1.0/np.sum(clus_list))
    #     mean_matching.append(np.sum(match_list)*1.0/(np.sum(clus_list)+zero_count))
    
    # print(mean_matching)

    # mean_matching = []
    # propnoun_list = []
    # commonnou_list = []
    # clus_list = []
    # zero_count = 0
    # with open("./Analysis_FT_Ontonotes_{}.json".format(1.0), "r") as f:
    #     stats_dict = json.load(f)

    # for each_doc in stats_dict:
    #     propnoun_list.append(stats_dict[each_doc]["propernoun_cluster_count"])
    #     commonnou_list.append(stats_dict[each_doc]["commonnoun_cluster_count"])
    #     clus_list.append(stats_dict[each_doc]["cluster_count"])

    #     if(stats_dict[each_doc]["commonnoun_cluster_count"]>20):
    #         import ipdb; ipdb.set_trace()


    # print(mean_matching)

    # print("done finding files", mean_matching)








if __name__ == "__main__":
    cluster_matching_analysis()
    # doc_len_analysis()
    # doc_size_analysis()