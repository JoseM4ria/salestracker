from rest_framework import viewsets
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, redirect


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


class GrupoProdutoViewSet(viewsets.ModelViewSet):
    queryset = GrupoProduto.objects.all()
    serializer_class = GrupoProdutoSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer


class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer


class VendaViewSet(viewsets.ModelViewSet):
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer

    @action(detail=False, methods=["get"])
    def relatorio(self, request):
        cliente_id = request.query_params.get("cliente")
        vendedor_id = request.query_params.get("vendedor")
        data = request.query_params.get("data")

        vendas = self.queryset
        if cliente_id:
            vendas = vendas.filter(cliente_id=cliente_id)
        if vendedor_id:
            vendas = vendas.filter(vendedor_id=vendedor_id)
        if data:
            vendas = vendas.filter(data_venda=data)

        serializer = self.get_serializer(vendas, many=True)
        return Response(serializer.data)


class ItensVendaViewSet(viewsets.ModelViewSet):
    queryset = ItensVenda.objects.all()
    serializer_class = ItensVendaSerializer


def index(request):
    context = {"clientes": Cliente.objects.all(), "vendedores": Vendedor.objects.all()}
    return render(request, "core/index.html", context)


def relatorio_vendas(request):
    vendas = Venda.objects.all()

    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    vendedor = request.GET.get("vendedor")
    cliente = request.GET.get("cliente")

    if data_inicio:
        vendas = vendas.filter(data_venda__gte=data_inicio)
    if data_fim:
        vendas = vendas.filter(data_venda__lte=data_fim)
    if vendedor:
        vendas = vendas.filter(vendedor_id=vendedor)
    if cliente:
        vendas = vendas.filter(cliente_id=cliente)

    for venda in vendas:
        venda.valor_total = sum(
            item.quantidade * item.produto.valor for item in venda.itens.all()
        )
        venda.save(update_fields=["valor_total"])

    context = {"vendas": vendas}
    return render(request, "core/relatorio_vendas.html", context)


def cliente_create(request):
    if request.method == "POST":
        nome = request.POST["nome"]
        email = request.POST["email"]
        telefone = request.POST["telefone"]
        Cliente.objects.create(nome=nome, email=email, telefone=telefone)

        return redirect("/")

    return render(request, "core/cliente_create.html")


def vendedor_create(request):
    if request.method == "POST":
        nome = request.POST["nome"]
        registro = request.POST["registro"]
        # Lógica para salvar o vendedor no banco de dados
        vendedor = Vendedor.objects.create(nome=nome, registro=registro)
        return redirect("core:vendedor_create")
    return render(request, "core/vendedores_create.html")


def produto_create(request):
    if request.method == "POST":
        nome = request.POST["nome"]
        grupo = request.POST["grupo"]
        Vendedor.objects.create(nome=nome, registro=grupo)

        return redirect("/")

    return render(request, "core/vendedores_create.html")


def cadastrar_venda(request):
    if request.method == "POST":
        cliente_id = request.POST.get("cliente")
        vendedor_id = request.POST.get("vendedor")
        produtos = request.POST.getlist("produtos[]")
        quantidades = request.POST.getlist("quantidades[]")

        if not cliente_id or not vendedor_id or not produtos or not quantidades:
            return render(
                request,
                "core/cadastrar_venda.html",
                {
                    "error": "Todos os campos são obrigatórios!",
                    "clientes": Cliente.objects.all(),
                    "vendedores": Vendedor.objects.all(),
                    "produtos": Produto.objects.all(),
                },
            )

        cliente = Cliente.objects.get(id=cliente_id)
        vendedor = Vendedor.objects.get(id=vendedor_id)
        venda = Venda.objects.create(cliente=cliente, vendedor=vendedor)

        for produto_id, quantidade in zip(produtos, quantidades):
            try:
                produto = Produto.objects.get(id=produto_id)
                if int(quantidade) > 0:
                    ItensVenda.objects.create(
                        venda=venda, produto=produto, quantidade=int(quantidade)
                    )
            except (Produto.DoesNotExist, ValueError):
                continue

        venda.calcular_valor_total()
        venda.save(update_fields=["valor_total"])
        return redirect("/relatorios/vendas/")

    context = {
        "clientes": Cliente.objects.all(),
        "vendedores": Vendedor.objects.all(),
        "produtos": Produto.objects.all(),
    }
    return render(request, "core/cadastrar_venda.html", context)
