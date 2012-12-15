import csv
from igraph import *

csv_file = "C:\\scrapy_sandbox\\tutorial\\items.csv"
num_users = 125000
isWeighted = True
topN = 100
graph_file = "users.gml"

def create_dict(csv_file,user_dict,topic_dict,num_users):
    with open(csv_file,'r') as csvfile:
        readBuffer = csv.reader(csvfile)
        for i,row in enumerate(readBuffer):
            if (i > 0) and (len(user_dict) < num_users):# and (row[0] == '51'):
                if (row[6] in user_dict):
                    #modify user
                    if row[0] not in user_dict[row[6]]['boards']:
                        user_dict[row[6]]['boards'].add(row[0])
                    if row[3] not in user_dict[row[6]]['topics']:
                        user_dict[row[6]]['topics'].add(row[3])
                    if(row[5]=='True'):
                        user_dict[row[6]]['op_count'] += 1
                    user_dict[row[6]]['post_count'] +=1
                else:
                    #create user
                    user_dict[row[6]] = {}
                    user_dict[row[6]]['boards'] = {row[0]}
                    user_dict[row[6]]['topics'] = {row[3]}
                    if(row[5]=='True'):
                        user_dict[row[6]]['op_count'] = 1
                    else:
                        user_dict[row[6]]['op_count'] = 0
                    user_dict[row[6]]['post_count'] = 1
                if (row[3] in topic_dict):
                    #modify topic
                    if row[6] not in topic_dict[row[3]]['users']:
                        topic_dict[row[3]]['users'].add(row[6])
                    topic_dict[row[3]]['posts'] += 1
                else:
                    #create topic
                    topic_dict[row[3]] = {}
                    topic_dict[row[3]]['users'] = {row[6]}
                    topic_dict[row[3]]['posts'] = 1
                    topic_dict[row[3]]['board'] = row[0]

    print "# of Users = "+str(len(user_dict))
    print "# of Topics = "+str(len(topic_dict))

def add_node(graph, user, index):
    graph.vs[index]['label'] = user
    graph.vs[index]['post_count'] = user_dict[user]['post_count']
    graph.vs[index]['op_count'] = user_dict[user]['op_count']

def add_edge(graph,n1,n2,edge_weight):
    graph.add_edges((n1,n2))
    graph.es[len(graph.es)-1]['weight']=edge_weight


def create_full_gml(graph_file,user_dict,isWeighted):
    g = Graph(len(user_dict))
    with open(graph_file,'w') as gmlfile:
       # gmlfile.write("graph [\n\t directed 0\n")
        for i,user in enumerate(user_dict.keys()):
            node = "\tnode [\n\t\tid "+str(i)+"\n\t\tlabel \""+user+"\"\n\t\top_count "+str(user_dict[user]['op_count'])+"\n\t\tpost_count "+str(user_dict[user]['post_count'])+"\n\t]\n"
            add_node(g,user,i)
       #     gmlfile.write(node)
            #print node
        num_edges = 0
        max_edge_weight = 0
        for i,user in enumerate(user_dict.keys()):
            for j,other in enumerate(user_dict.keys()):
                if j>i:                    
                    edge_weight = len(user_dict[user]['topics'].intersection(user_dict[other]['topics']))
                    if edge_weight > 0:
                        if edge_weight > max_edge_weight:
                            max_edge_weight = edge_weight
                        num_edges += 1;
                        if not isWeighted:
                            edge = "\tedge [\n\t\tsource "+str(i)+"\n\t\ttarget "+str(j)+"\n\t]\n"
                            add_edge(g,i,j,1)
                        else:
                            edge = "\tedge [\n\t\tsource "+str(i)+"\n\t\ttarget "+str(j)+"\n\t\tweight "+str(edge_weight)+"\n\t]\n"
                            add_edge(g,i,j,edge_weight)
      #                  gmlfile.write(edge)
       # gmlfile.write("]")
                        #print edge

    print "Edges = "+str(num_edges)
    print "Max Weight = "+str(max_edge_weight)

def create_user_gml(graph_file,user_dict,isWeighted,usernames):
    nodes = list(usernames)
    with open(graph_file,'w') as gmlfile:
        gmlfile.write('graph [\n\t directed 0\n')
        for username in usernames:
#            print username
            node = "\tnode [\n\t\tid "+username+"\n\t\tlabel \""+username+"\"\n\t\top_count "+str(user_dict[username]['op_count'])+"\n\t\tpost_count "+str(user_dict[username]['post_count'])+"\n\t]\n"
            gmlfile.write(node)
            for user in user_dict.keys():
                if (user_dict[username]['topics'].intersection(user_dict[user]['topics'])) and (user not in nodes):
#                    print user
 #                   print username
  #                  print (user_dict[username]['topics'].intersection(user_dict[user]['topics']))
                    nodes.append(user)
                    node = "\tnode [\n\t\tid "+user+"\n\t\tlabel \""+user+"\"\n\t\top_count "+str(user_dict[user]['op_count'])+"\n\t\tpost_count "+str(user_dict[user]['post_count'])+"\n\t]\n"
                    gmlfile.write(node)
#        print nodes
        print len(nodes)
        for i,node in enumerate(nodes):
            for j,other in enumerate(nodes):
                if j>i:
                    edge_weight = len(user_dict[node]['topics'].intersection(user_dict[other]['topics']))
                    if edge_weight > 0:
                        if not isWeighted:
                            edge = "\tedge [\n\t\tsource "+node+"\n\t\ttarget "+other+"\n\t]\n"
                        else:
                            edge = "\tedge [\n\t\tsource "+node+"\n\t\ttarget "+other+"\n\t\tweight "+str(edge_weight)+"\n\t]\n"
                        gmlfile.write(edge)
        gmlfile.write("]")

def create_most_active_users_gml(graph_file,user_dict,isWeighted,topN,param):
    usernames = []
    values = []
    for i,user in enumerate(user_dict.keys()):
        if (param == 'post_count'):
            val = user_dict[user]['post_count']
        else:
            val = len(user_dict[user][param])
        if i < topN:
            usernames.append(user)
            values.append(val)
        elif val >= max(values):
            print usernames
            print values
            toRemove = usernames[values.index(min(values))]
            usernames.remove(toRemove)
            values.remove(min(values))
            usernames.append(user)
            values.append(val)
    create_user_gml(graph_file,user_dict,isWeighted,usernames)

def create_full_igraph(user_dict,isWeighted):
    g = Graph(len(user_dict))
    for i,user in enumerate(user_dict.keys()):
        add_node(g,user,i)
##        for topic in user_dict[user]['topics']:
##            if len(topic_dict[topic]['users']) > 1:
##                add_node(g,user,i)
##                break
    print "nodes made"
    num_edges = 0
    for i,topic in enumerate(topic_dict.keys()):
#    for topic in ['482857']:
        nodes2connect = []
        num_users_in_topic = 0
        for user in topic_dict[topic]['users']:
            nodes2connect.append(user_dict.keys().index(user))
            num_users_in_topic += 1
            print user
        print "#users in topic:"+str(num_users_in_topic)
        if num_users_in_topic > 1:
            for n1 in range(0,len(nodes2connect)-1):
                for n2 in range(n1+1,len(nodes2connect)):
                    if ((nodes2connect[n1],nodes2connect[n2]) in (g.get_edgelist())):
                        g.es[g.get_edgelist().index((nodes2connect[n1],nodes2connect[n2]))]['weight'] +=1
                        print"here"+str(nodes2connect[n1])+"_"+str(nodes2connect[n2])
                    elif ((nodes2connect[n2],nodes2connect[n1]) in (g.get_edgelist())):
                        g.es[g.get_edgelist().index((nodes2connect[n2],nodes2connect[n1]))]['weight'] +=1
                        print"here2"+str(nodes2connect[n2])+"_"+str(nodes2connect[n1])
                    else:
                        num_edges += 1
                        add_edge(g,nodes2connect[n1],nodes2connect[n2],1)
                        print str(nodes2connect[n1])+"_"+str(nodes2connect[n2])
                        print num_edges
        print "topic#"+str(i)+" of 148222"
    print "Edges = "+str(num_edges)
    return g
            
    

            
user_dict = dict()
topic_dict = dict()
create_dict(csv_file,user_dict,topic_dict,num_users)
#create_full_gml(graph_file,user_dict,isWeighted)

        
    
#boards
#topics
#op_count
#in
#out
